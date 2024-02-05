import os.path as op
import numpy
import torch
from torch_geometric.data import InMemoryDataset
from rdkit import Chem
from rdkit.Chem import MolFromSmiles
from tqdm import tqdm


class GNNDataset(InMemoryDataset):
    def __init__(self):
        def __init__(self, root, train=True, transform=None, pre_transform=None, pre_filter=None):
            super().__init__(root, transform, pre_transform, pre_filter)
            if train:
                self.data, self.slices = torch.load(self.processed_paths[0])
            else:
                self.data, self.slices = torch.load(self.processed_paths[1])

    pass