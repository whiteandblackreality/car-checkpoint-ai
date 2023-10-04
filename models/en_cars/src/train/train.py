import yaml
from src.train.model_trainers import CarsVerificationModelTrainer
import warnings
warnings.filterwarnings("ignore")

TRAIN_RUN_CONFIG = '../configs/train_run_config.yaml'

def run_train():
    with open(TRAIN_RUN_CONFIG, 'r') as fin:
        opt_run = yaml.safe_load(fin.read())

    with open(opt_run['model_config'], 'r') as fin:
        model_config = yaml.safe_load(fin.read())

    with open(opt_run['data_config'], 'r') as fin:
        data_config = yaml.safe_load(fin.read())

    with open(opt_run['train_config'], 'r') as fin:
        train_config = yaml.safe_load(fin.read())

    model_trainer = CarsVerificationModelTrainer(model_config=model_config, data_config=data_config,
                                        train_config=train_config)

    model_trainer.train()


if __name__ == '__main__':
    run_train()