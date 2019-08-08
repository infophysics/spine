# GNN that attempts to match clusters to groups
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import torch
import numpy as np
from torch.nn import Sequential as Seq, Linear as Lin, ReLU, Sigmoid, LeakyReLU, Dropout, BatchNorm1d
from torch_geometric.nn import MetaLayer, GATConv

class BasicAttentionModel(torch.nn.Module):
    """
    Simple GNN with several edge convolutions, followed by MetLayer for edge prediction
    
    for use in config
    model:
        modules:
            attention_gnn:
                nheads: <number of heads for attention>
    """
    def __init__(self, cfg):
        super(BasicAttentionModel, self).__init__()
        
        
        if 'modules' in cfg:
            self.model_config = cfg['modules']['attention_gnn']
        else:
            self.model_config = cfg

        self.nheads = self.model_config.get('nheads', 3)
        self.leak = self.model_config.get('leak', 0.1)
        
        # perform batch normalization at each step
        self.bn_node = BatchNorm1d(16)
        
        # first layer increases number of features from 4 to 16
        # self.attn1 = GATConv(4, 16, heads=self.nheads, concat=False)
        # first layer increases number of features from 15 to 16
        self.attn1 = GATConv(16, 16, heads=self.nheads, concat=False)
        
        # second layer increases number of features from 16 to 32
        self.attn2 = GATConv(16, 32, heads=self.nheads, concat=False)
        
        # third layer increases number of features from 32 to 64
        self.attn3 = GATConv(32, 64, heads=self.nheads, concat=False)
        
        self.bn_edge = BatchNorm1d(10)

        # final prediction layer
        class EdgeModel(torch.nn.Module):
            def __init__(self, leak):
                super(EdgeModel, self).__init__()

                self.edge_pred_mlp = Seq(Lin(138, 64),
                                         LeakyReLU(leak),
                                         Lin(64, 32),
                                         LeakyReLU(leak),
                                         Lin(32, 16),
                                         LeakyReLU(leak),
                                         Lin(16,8),
                                         LeakyReLU(leak),
                                         Lin(8,2)
                                        )

            def forward(self, src, dest, edge_attr, u, batch):
                return self.edge_pred_mlp(torch.cat([src, dest, edge_attr], dim=1))
        
        self.edge_predictor = MetaLayer(EdgeModel(self.leak))
        
        
    def forward(self, x, edge_index, e, xbatch):
        """
        inputs data:
            x - vertex features
            edge_index - graph edge list
            e - edge features
            xbatch - node batchid
        """
        
        # batch normalization of node features
        x = self.bn_node(x)
        
        # batch normalization of edge features
        e = self.bn_edge(e)
        
        # go through layers
        x = self.attn1(x, edge_index)

        x = self.attn2(x, edge_index)

        x = self.attn3(x, edge_index)
        
        x, e, u = self.edge_predictor(x, edge_index, e, u=None, batch=xbatch)

        return [[e]]
