import torch
from torch import nn


def get_torch_adamW(model: nn.Module, optim_parameters: dict):
    """ Function for determining the AdamW optimizer """
    return torch.optim.AdamW(params=model.parameters(), **optim_parameters)


def get_one_cycle_scheduler(optimizer: torch.optim.Optimizer, scheduler_params: dict):
    """ Function for defining the learning_rate OneCycle schedule """
    return torch.optim.lr_scheduler.OneCycleLR(optimizer=optimizer, **scheduler_params)


def get_optimizer(optim_name: str, model: nn.Module, optim_parameters: dict):
    """ Function to get the required optimizer """
    optim_mappings = {'AdamW': get_torch_adamW(model, optim_parameters)}

    return optim_mappings[optim_name]


def get_scheduler(scheduler_name: str, optimizer: torch.optim.Optimizer, scheduler_params: dict):
    """ Function to get the required schedule learning_rate """
    scheduler_mapping = {'OneCycle': get_one_cycle_scheduler}

    return scheduler_mapping[scheduler_name](optimizer=optimizer, scheduler_params=scheduler_params)