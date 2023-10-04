from torchvision import transforms

def torch_resize(resize_shape: tuple):
    """ Function for defining transforms.Resize - changing the image size """
    return transforms.Resize((resize_shape, resize_shape))

def torch_h_flip(p: float):
    """ Function for defining transforms.Random Horizontal Flip - Image Mirroring """
    return transforms.RandomHorizontalFlip(p)

def torch_rotation(p: float, degrees: int):
    """ Function for defining transforms.RandomRotation - random rotation of the image (-degrees, degrees) """
    return transforms.RandomApply([transforms.RandomRotation(degrees)], p)

def get_torch_transform(transform_name: str, transform_parameters: dict):
    """ Function for selecting a specific type of image conversion """

    transform_mapping = {'resize': torch_resize,
                         'h_flip': torch_h_flip,
                         'rotation': torch_rotation}

    return transform_mapping[transform_name](**transform_parameters)


def get_transforms_compose(transform: dict):
    """ Function of combining all transformations over the image """
    compose = [get_torch_transform(transform_name, transform_parameters)
                                    for transform_name, transform_parameters in transform.items()]
    compose.append(transforms.ToTensor())
    return transforms.Compose(compose)