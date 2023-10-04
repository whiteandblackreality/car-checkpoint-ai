import torch
from torch import nn
from torch.autograd import Variable
from torch.nn import functional as F


class FocalLoss(nn.Module):
    """ FocalLoss class
        https://paperswithcode.com/method/focal-loss
    Attributes:
        class_num: number of classes
        alpha: weights for each class
        gamma: gamma parameter
        size_average: Flag of error averaging by butch
        device: GPU device number
    """

    def __init__(self, class_num: int, alpha=None, gamma=2, size_average=True, device: str = 'cpu'):
        super(FocalLoss, self).__init__()
        if alpha is None:
            self.alpha = Variable(torch.ones(class_num, 1))
        else:
            if isinstance(alpha, Variable):
                self.alpha = alpha
            else:
                self.alpha = Variable(alpha)
        self.gamma = gamma
        self.class_num = class_num
        self.size_average = size_average
        self.device = device

    def forward(self, inputs, targets):
        N = inputs.size(0)
        C = inputs.size(1)
        P = F.softmax(inputs, dim=1)

        class_mask = inputs.data.new(N, C).fill_(0)
        class_mask = Variable(class_mask)
        ids = targets.view(-1, 1)
        class_mask.scatter_(1, ids.data, 1.)

        if inputs.is_cuda and not self.alpha.is_cuda:
            self.alpha = self.alpha.to(self.device)
        alpha = self.alpha[ids.data.view(-1)]

        probs = (P * class_mask).sum(1).view(-1, 1)

        log_p = probs.log()

        batch_loss = -alpha * (torch.pow((1 - probs), self.gamma)) * log_p

        if self.size_average:
            loss = batch_loss.mean()
        else:
            loss = batch_loss.sum()
        return loss

def get_cross_entropy_loss(loss_params: dict):
    """ Function for determining the CrossEnropyLoss loss function """
    if loss_params != 'None':
        return nn.CrossEntropyLoss(**loss_params)
    else:
        return nn.CrossEntropyLoss()


def get_focal_loss(loss_params: dict):
    """ Function for determining the FocalLoss loss function """
    return FocalLoss(**loss_params)


def get_loss_func(loss_name: str, loss_params: dict):
    """ Function for selecting a specific loss function """
    loss_mapping = {'CE': get_cross_entropy_loss,
                    'Focal': get_focal_loss}

    return loss_mapping[loss_name](loss_params)
