import timm

import torch
import torch.nn as nn
import torch.nn.functional as F

import math


class ArcFace(nn.Module):

    def __init__(self, in_features, out_features, scale_factor=64.0, margin=0.50, criterion=None):
        super(ArcFace, self).__init__()
        self.in_features = in_features
        self.out_features = out_features

        self.margin = margin
        self.scale_factor = scale_factor

        self.weight = nn.Parameter(
            torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)

        self.cos_m = math.cos(margin)
        self.sin_m = math.sin(margin)
        self.th = math.cos(math.pi - margin)
        self.mm = math.sin(math.pi - margin) * margin

    def forward(self, input, label):

        cosine = F.linear(F.normalize(input), F.normalize(self.weight))
        sine = torch.sqrt(1.0 - torch.pow(cosine, 2))

        phi = cosine * self.cos_m - sine * self.sin_m
        phi = phi.type(cosine.type())
        phi = torch.where(cosine > self.th, phi, cosine - self.mm)

        one_hot = torch.zeros(cosine.size(), device=input.device)
        one_hot.scatter_(1, label.view(-1, 1).long(), 1)

        logit = (one_hot * phi) + ((1.0 - one_hot) * cosine)
        logit *= self.scale_factor

        return logit


class CarsModel(nn.Module):
    """ Cars model class, based on method ArcFace
    Attributes:
        backbone_name: backbone model name
        num_classes: number of classes
        emb_size: output embeddings size
        scale: ArcFace sacle parameter
        margin: ArcFace margin parameter
    """

    def __init__(self, backbone_name: str, num_classes: int, emb_size: int,
                 scale: int, margin: float, drop_rate: float = 0):
        super(CarsModel, self).__init__()

        self.cnn_model = timm.create_model(backbone_name, pretrained=True)
        self.cnn_model.reset_classifier(emb_size, global_pool='avg')

        self.dropout = nn.Dropout(drop_rate)

        self.arc = ArcFace(
            in_features=emb_size,
            out_features=num_classes,
            scale_factor=scale,
            margin=margin
        )

    def forward(self, x, labels=None):
        features = self.cnn_model(x)
        emb = self.dropout(features)

        if labels is not None:
            output = self.arc(emb, labels)
            return emb, output

        else:
            return emb



