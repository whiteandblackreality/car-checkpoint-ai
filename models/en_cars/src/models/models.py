import numpy as np
from torch import nn
import torch


from sklearn.metrics.pairwise import cosine_similarity
from src.models.cars_model import CarsModel




class VerificationCarsModel:
    """ VerificationCarsModel class
    Attributes:
        cars_model_parameters: CarsModel parameters
        gpus: list of GPU device numbers
        emb_size: embedding output size
        weights: path fow model weights (if None use ' ')
        """

    def __init__(self, cars_model_parameters: dict, gpus: list, emb_size: int, weights: str):

        self.cars_model_parameters = cars_model_parameters
        self.gpus = gpus
        self.emb_size = emb_size
        self.weights = weights

        self.load_model()


    def load_model(self):
        """ Load model  """
        if self.weights != '':
            self.model = torch.load(self.weights, map_location='cpu')
        else:
            self.model = CarsModel(**self.cars_model_parameters)

        if len(self.gpus) == 1:
            self.device = f'cuda:{self.gpus[0]}'
            self.model = self.model.to(self.device)
        else:
            self.device = 'cuda'
            self.model = nn.DataParallel(self.model, device_ids=self.gpus)
            self.model.to(self.device)



def get_model(model_name: str, model_parameters: dict):
    """ Get model function
    Arguments:
        model_name: model name
        model_parameters: model parameters
    """
    model_mapping = {'cars_model': VerificationCarsModel(**model_parameters)}

    return model_mapping[model_name]