# DurgSolAtten: An Interpretable Hybrid Predictive Framework for Organic Drug Solubility Enhancement via Graph Convolutional Networks and Transformer-Attention Modules

<img width="779" alt="image" src="https://github.com/xunyoyo/YZS-Model/assets/33387866/b0b34260-67ac-4d64-971f-93f009c4eb40">



## Configuration of the DurgSolAtten environment

```
python==3.6
torch==1.7.1
scikit-learn==0.24.2
scipy==1.5.4
torch-geometric==1.7.0
einops==0.4.1
networkx==2.5.1
rdkit-pypi
```

Other packages can be found from `requirements.txt`.

## Datasets

You can download the training and testing dataset from:

[All datasets in the raw folders.](https://github.com/xunyoyo/YZS-Model/tree/main/Datasets)

## Useage

+ `smile2topology.py`: Convert .csv files to datasets.
+ `model.py`: The whole YZS-model.
+ `opti.py`: Using searching package to find the perfect parameters.
+ `train.py`: Training the YZS-model.
+ `test.py`:Tests and evaluates the YZS model.

## About

authors:
+ Chenxu Wang, Shihezi University (PRC, Xinjiang)
    + e-mail:zxsdsama@gmail.com
+ Haowei Ming, Peking University (PRC, Beijing)
+ Jian He, Xinjiang University (PRC, Xinjiang)
+ Junhong Chen, {South China University of Technology, NetEase Inc.} (PRC, {Guangdong, Zhejiang})

Statement:
+ Part of code come from:
```
https://github.com/ziduzidu/CSDTI
https://github.com/ltorres97/FS-CrossTR
https://github.com/waqarahmadm019/AquaPred
```
When using the above-mentioned open-source code, we have already indicated this in the documents.
