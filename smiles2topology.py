import os.path as op
import numpy
import pandas as pd
import torch
from torch_geometric.data import InMemoryDataset
from torch_geometric import data as DATA
import networkx as nx
from rdkit import Chem
from rdkit.Chem import MolFromSmiles
from rdkit.Chem import ChemicalFeatures
from rdkit import RDConfig
from tqdm import tqdm

fdef_name = op.join(RDConfig.RDDataDir, 'BaseFeatures.fdef')
chem_feature_factory = ChemicalFeatures.BuildFeatureFactory(fdef_name)


class MyOwnDataset(InMemoryDataset):

    def __init__(self, root, train=True, transform=None, pre_transform=None, pre_filter=None):
        super().__init__(root, transform, pre_transform, pre_filter)
        if train:
            self.data, self.slices = torch.load(self.processed_paths[0])
        else:
            self.data, self.slices = torch.load(self.processed_paths[1])

    @property
    def raw_file_names(self):
        return ['data_train.csv']

    @property
    def processed_file_names(self):
        return ['processed_data_train.pt']

    def download(self):
        pass

    def pre_process(self, data_path, data_dict):
        file = pd.read_csv(data_path)

        data_lists = []
        for index, row in file.iterrows():
            smiles = row['isomeric_smiles']
            logS = row['logS0']

            x, edge_index, edge_index2, edge_attr = data_dict[smiles]

            if x.max() == x.min():
                x = (x - x.min()) / 0.000001
            else:
                x = (x - x.min()) / (x.max() - x.min())

            try:
                data = DATA.Data(
                    x = x,
                    edge_index = edge_index,
                    edge_index2 = edge_index2,
                    edge_attr = edge_attr,
                    y = torch.FloatTensor([logS])
                )
            except:
                print("这个SMILE无法处理: ", smiles)

            data_lists.append(data)

        return data_lists

    def process(self):
        file_train = pd.read_csv(self.raw_paths[0])
        file = file_train

        smiles = file['isomeric_smiles'].unique()
        graph_dict = dict()

        for smile in tqdm(smiles, total=len(smiles)):
            mol = Chem.MolFromSmiles(smile)
            g = self.mol2graph(mol)
            graph_dict[smile] = g

        train_list = self.pre_process(self.raw_paths[0], graph_dict)

        if self.pre_filter is not None:
            train_list = [train for train in train_list if self.pre_filter(train)]
            # test_list = [test for test in test_list if self.pre_filter(test)]

        if self.pre_transform is not None:
            train_list = [self.pre_transform(train) for train in train_list]
            # test_list = [self.pre_transform(test) for test in test_list]

        print("图建完了。")

        data, slices = self.collate(train_list)
        torch.save((data, slices), self.processed_paths[0])


    def mol2graph(self, mol):
        if mol is None:
            return None

        features = chem_feature_factory.GetFeaturesForMol(mol)
        graph = nx.DiGraph()

        # 创建点
        for i in range(mol.GetNumAtoms()):
            atom_i = mol.GetAtomWithIdx(i)

            """
            atom_symbol: 原子符号
            atom_id: 原子序号
            is_aromatic: 是否芳香
            hybridization: 杂化情况
            FormalCharge: 形式电荷情况
            IsInRing: 是否在环中
            待定ing
            """
            graph.add_node(
                i,
                atom_symbol=atom_i.GetSymbol(),
                atom_id=atom_i.GetAtomicNum(),
                is_aromatic=atom_i.GetIsAromatic(),
                hybridization=atom_i.GetHybridization(),
                num_h=atom_i.GetTotalNumHs(),
                FormalCharge=atom_i.GetFormalCharge(),
                IsInRing=atom_i.IsInRing(),
                # acceptor=0,
                # donor=0,
                #
                #
                # # 5 more node features
                # ExplicitValence=atom_i.GetExplicitValence(),
                # ImplicitValence=atom_i.GetImplicitValence(),
                # NumExplicitHs=atom_i.GetNumExplicitHs(),
                # NumRadicalElectrons=atom_i.GetNumRadicalElectrons(),
            )

        # 连接边
        for i in range(mol.GetNumAtoms()):
            for j in range(mol.GetNumAtoms()):
                e_ij = mol.GetBondBetweenAtoms(i, j)
                if e_ij is not None:

                    """
                    bond_type: 键的类型
                    IsConjugated: 是否共轭
                    
                    """
                    graph.add_edge(
                        i, j,
                        bond_type=e_ij.GetBondType(),
                        IsConjugated=int(e_ij.GetIsConjugated()),
                    )

        node_attr = self.get_nodes(graph)
        edge_index, edge_attr = self.get_edges(graph)
        edge_index2 = self.get_2hop(graph)

        return node_attr, edge_index, edge_index2, edge_attr

    def get_nodes(self, graph):
        feature = []

        for node, feat in graph.nodes(data=True):
            h_t = []
            # 元素符号作为标记加入特征
            h_t += [int(feat['atom_symbol'] == x) for x in ['H', 'C', 'N', 'O', 'F', 'Cl', 'S', 'Br', 'I', 'P']]
            h_t.append(feat['atom_id'])
            h_t.append(int(feat['is_aromatic']))
            h_t += [int(feat['hybridization'] == x)
                    for x in (Chem.rdchem.HybridizationType.SP,
                              Chem.rdchem.HybridizationType.SP2,
                              Chem.rdchem.HybridizationType.SP3)
                    ]
            h_t.append(feat['FormalCharge'])
            h_t.append(int(feat['IsInRing']))
            feature.append((node, h_t))

        feature.sort(key=lambda item: item[0])
        node_attr = torch.FloatTensor([item[1] for item in feature])

        return node_attr

    def get_edges(self, graph):
        edge = {}
        for u, v, feat in graph.edges(data=True):
            e_t=[int(feat['bond_type'] == x)
                for x in (Chem.rdchem.BondType.SINGLE,
                          Chem.rdchem.BondType.DOUBLE,
                          Chem.rdchem.BondType.TRIPLE,
                          Chem.rdchem.BondType.AROMATIC)
                ]
            e_t.append(int(feat['IsConjugated'] == False))
            e_t.append(int(feat['IsConjugated'] == True))
            edge[(u, v)] = e_t

        if len(edge) == 0:
            return torch.LongTensor([[0], [0]]), torch.FloatTensor([[0, 0, 0, 0, 0, 0]])

        edge_index = torch.LongTensor(list(edge.keys())).transpose(0, 1)
        edge_attr = torch.FloatTensor(list(edge.values()))
        return edge_index, edge_attr

    def get_2hop(self, graph):
        As = nx.adjacency_matrix(graph)
        As = As.dot(As)
        edge_index2 = torch.LongTensor(As.nonzero())
        return edge_index2

if __name__ == "__main__":
    MyOwnDataset('Datasets')