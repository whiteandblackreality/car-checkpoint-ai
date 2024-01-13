import torch
from PIL import Image
from torchvision import transforms

from models.vehicle_recognition.models.arc_face import CarsModel


class VerificationCarsModel:
    """ VerificationCarsModel class
    Attributes:
        cars_model_parameters: CarsModel parameters
        gpus: list of GPU device numbers
        emb_size: embedding output size
        weights: path fow model weights (if None use '')
        """

    def __init__(self, cars_model_parameters: dict, gpus: int, emb_size: int, weights: str):

        self.cars_model_parameters = cars_model_parameters
        self.gpus = gpus
        self.emb_size = emb_size
        self.weights = weights

        self.load_model()

    def preprocess(self, img: Image, resize: int = 512):

        torch_img = transforms.Compose([transforms.ToTensor(),
                                        transforms.Resize((resize, resize), antialias=True)],)(img)

        return torch_img.view(1, 3, resize, resize).to(self.device)

    def load_model(self):

        if self.weights != '':
            self.model = torch.load(self.weights, map_location='cpu').module
        else:
            self.model = CarsModel(**self.cars_model_parameters)
        self.device = f'cuda:{self.gpus}'
        self.model = self.model.to(self.device)

    @torch.no_grad()
    def __call__(self, img: Image, resize: int = 512):
        self.model.eval()
        #img = self.preprocess(img, resize)

        emb = self.model(img).detach().cpu().numpy()

        return emb


def get_model(model_name: str, model_parameters: dict):
    """ Get model function
    Arguments:
        model_name: model name
        model_parameters: model parameters
    """
    model_mapping = {'cars_model': VerificationCarsModel(**model_parameters)}

    return model_mapping[model_name]
