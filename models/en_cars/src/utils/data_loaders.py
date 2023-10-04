from torch.utils.data import DataLoader, Dataset

from PIL import Image
import numpy as np

import pandas as pd


import imgaug.augmenters as iaa
import random

from src.utils.pytorch_transforms import get_transforms_compose

import os


class CarsDataset(Dataset):
    """ Cars images dataset calss
    Attributes:
        root_path: path to data
        sample_type: train or val
        path_csv: path to csv with data
        transform: image augmentaion
        img_aug: Cutout augmentation
        """

    def __init__(self, root_path: str, sample_type: str, df_path: str, transform: dict, imgaug_cutout=False):

        self.root_path = root_path
        self.sample_type = sample_type
        self.df = pd.read_csv(df_path, low_memory=False)

        self.get_transform(transform)

        self.img_aug = imgaug_cutout

        self.class2label = {cls: idx for idx, cls in enumerate(self.df['class'].unique())}
        self.label2class = {idx: cls for cls, idx in self.class2label.items()}


    def get_transform(self, transform: dict):
        self.transform = get_transforms_compose(transform)

    def __len__(self):
        return self.df.shape[0]

    def __imgaug(self, image: Image, p=0.3, nb_iterations=10, size=0.1):
        """ Метод для выполения аугментации CutOut """
        try:
            if random.random() < p:
                img_arr = np.array(image)
                img_arr = iaa.Cutout(nb_iterations=nb_iterations, size=size).augment_image(img_arr)
                image = Image.fromarray(img_arr.astype('uint8'), 'RGB')
        except:
            print('Cant img_aug')

        return image

    def __getitem__(self, idx):
        try:
            img = Image.open(os.path.join(self.root_path, self.df.iloc[idx].image_name)).convert('RGB')
        except:
            print('Cant read image')
            idx = 0
            img = Image.open(os.path.join(self.root_path, self.df.iloc[idx].image_name)).convert('RGB')

        label = self.class2label[self.df.iloc[idx]['class']]

        x_1 = self.df.iloc[idx].x_1
        x_2 = self.df.iloc[idx].x_2
        y_1 = self.df.iloc[idx].y_1
        y_2 = self.df.iloc[idx].y_2

        try:
            crop_image = img.crop((x_1, y_1, x_2, y_2))
        except:
            crop_image = img

        if self.img_aug:
            crop_image = self.__imgaug(image=crop_image)

        torch_img = self.transform(crop_image)

        if self.sample_type == 'train':
            return torch_img, label

        elif self.sample_type == 'val':
            return torch_img, label, self.df.iloc[idx].image_name


def get_dataset(dataset_name: str):
    """ Function for selecting a specific dataset
    Arguments:
        dataset_name: Dataset name
    """
    dataset_mapping = {'cars_dataset': CarsDataset}

    return dataset_mapping[dataset_name]

def get_data_loader(dataset_name: str, dataset_parameters: dict, batch_size: int, num_workers: int,
                    shuffle: bool):
    """ Function for selecting a specific dataloader
    Arguments:
        dataset_name: Dataset name
        dataset_parameters: Dataset parameters
        batch_size: batch size
        num_workers: number od workers
        shuffle: Flag - mixing of data
    :returns
        dataset: Dataset
        dataloader: DataLoader
    """
    dataset = get_dataset(dataset_name)(**dataset_parameters)

    dataloader = DataLoader(dataset=dataset, batch_size=batch_size, num_workers=num_workers,
                            shuffle=shuffle)

    return dataloader, dataset

