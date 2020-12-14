# Topic modelling on Tatar news dataset
This repository includes:
* parser's code for https://tatar-inform.tatar/ website
* [Attention-Based Aspect Extraction](https://www.aclweb.org/anthology/P17-1036.pdf) and [LDA](https://dl.acm.org/doi/pdf/10.5555/944919.944937) models comparison on topic modelling task with collected dataset

## Data 
You can find the full dataset, word2vec embeddings and model weights in [[Download]](https://drive.google.com/drive/folders/1b3YjR6ouMOp42V03cC2UMH4hff_zX85D?usp=sharing). 

## Get started
```
$ pip install -r requirements.txt
$ jupyter notebook
```

## Cite
If you use the code, please consider citing original paper:
```
@InProceedings{he-EtAl:2017:Long2,
  author    = {He, Ruidan  and  Lee, Wee Sun  and  Ng, Hwee Tou  and  Dahlmeier, Daniel},
  title     = {An Unsupervised Neural Attention Model for Aspect Extraction},
  booktitle = {Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  month     = {July},
  year      = {2017},
  address   = {Vancouver, Canada},
  publisher = {Association for Computational Linguistics}
}
```

## Aknowledgements

* Attention Based Aspect Extraction implementation from https://github.com/alexeyev/abae-pytorch
* List of Tatar stopwords from https://github.com/aliiae/stopwords-tt