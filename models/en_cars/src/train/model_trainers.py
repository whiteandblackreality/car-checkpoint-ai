import torch

from src.utils.data_loaders import get_data_loader
from src.models.models import get_model
from src.utils.optimizers import get_optimizer, get_scheduler
from src.utils.losses import get_loss_func

import os
from tqdm import tqdm
import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score, precision_score, roc_curve


class CarsVerificationModelTrainer:
    """ Class for train HappyWhale models
    Attributes:
        model_config: model parameters
        data_config: data parameters
        train_config: train parameters
    """

    def __init__(self, model_config: dict, data_config: dict, train_config: dict):

        self.model_config = model_config
        self.data_config = data_config
        self.train_config = train_config

        self.get_data_loaders()
        self.get_model()
        self.set_train_parameters()



    def get_data_loaders(self):
        """ Get DataLoaders"""

        ## Defining a training dataset
        self.train_loader, self.trainset = get_data_loader(dataset_name=self.data_config['train_data']['dataset_name'],
                                                        dataset_parameters=self.data_config['train_data']['dataset_params'],
                                                        batch_size=self.train_config['train_batch'],
                                                        num_workers=self.train_config['num_workers'],
                                                        shuffle=True)

        ## Defining a validation dataset
        self.val_loader, self.valset = get_data_loader(dataset_name=self.data_config['val_data']['dataset_name'],
                                                      dataset_parameters=self.data_config['val_data']['dataset_params'],
                                                      batch_size=self.train_config['val_batch'],
                                                      num_workers=self.train_config['num_workers'],
                                                      shuffle=False)


        print('Train data size:', len(self.trainset))
        print('Val data size:', len(self.valset))
        print('Number of classes:', len(set(self.trainset.df['class'].values)))

        ## Adding the parameter of the number of classes for the DolgNet model
        if self.model_config['model_name'] == 'cars_model':
            self.model_config['model_parameters']['cars_model_parameters']['num_classes'] = len(set(self.trainset.df['class'].values))


        self.easy_val_pairs = pd.read_csv(self.data_config['val_pairs_data']['easy_val'])
        self.normal_val_pairs = pd.read_csv(self.data_config['val_pairs_data']['normal_val'])
        self.hard_val_pairs = pd.read_csv(self.data_config['val_pairs_data']['hard_val'])



    def set_train_parameters(self):
        """ Method for determining training parameters """

        self.optimizer = get_optimizer(optim_name=self.train_config['optimizer']['name'], model=self.model.model,
                                       optim_parameters=self.train_config['optimizer']['parameters'])
        if self.train_config['criterion']['name'] == 'Focal':
            self.train_config['criterion']['parameters']['device'] = self.model.device
            self.train_config['criterion']['parameters']['class_num'] = len(set(self.trainset.df['class'].values))
        self.criterion = get_loss_func(loss_name=self.train_config['criterion']['name'],
                                       loss_params=self.train_config['criterion']['parameters'])

        ## Adding a schedule for learning_rate
        if 'scheduler' in self.train_config:
            if self.train_config['scheduler']['name'] == 'OneCycle':
                self.train_config['scheduler']['parameters']['steps_per_epoch'] = len(self.train_loader)
                self.train_config['scheduler']['parameters']['epochs'] = self.train_config['num_epochs']
            self.scheduler = get_scheduler(scheduler_name=self.train_config['scheduler']['name'],
                                           optimizer=self.optimizer,
                                           scheduler_params=self.train_config['scheduler']['parameters'])

        else:
            self.scheduler = None

    def get_model(self):
        """ Model loading method """

        self.model = get_model(model_name=self.model_config['model_name'],
                               model_parameters=self.model_config['model_parameters'])



    def fit_epoch(self):
        """ Method for training a single learning epoch"""

        self.model.model.train()
        train_loss = []
        for idx, (imgs, labels) in tqdm(enumerate(self.train_loader)):
            imgs, labels = imgs.to(self.model.device), labels.to(self.model.device)

            self.optimizer.zero_grad()
            embs, output = self.model.model(imgs, labels)
            loss = self.criterion(output, labels)

            loss.backward()

            self.optimizer.step()

            if self.scheduler is not None:
                self.scheduler.step()

            train_loss.append(loss.item())
            if idx % 50 == 0:
                print('Train loss:', np.mean(train_loss))

        return np.mean(train_loss)

    def calculate_cosine_similarity(self, embs_1, embs_2):
        similarity = []
        for emb_1, emb_2 in zip(embs_1, embs_2):
            similarity.append(cosine_similarity(emb_1.reshape(1, -1), emb_2.reshape(1, -1))[0][0])

        return similarity

    def calculate_metrics(self, y_trues, y_probs):

        roc_auc = roc_auc_score(y_true=y_trues, y_score=y_probs)

        fpr, tpr, thresholds = roc_curve(y_trues, y_probs)
        optimal_idx = np.argmax(tpr - fpr)
        best_threshold = thresholds[optimal_idx]

        y_preds = (y_probs >= best_threshold).astype(int)

        recall = recall_score(y_trues, y_preds)
        precision = precision_score(y_trues, y_preds)
        acc = accuracy_score(y_trues, y_preds)

        result = {'roc_auc': roc_auc,
                  'best_thresh': best_threshold,
                  'recall': recall,
                  'precision': precision,
                  'acc': acc}

        return result

    @torch.no_grad()
    def eval_epoch(self):
        """ Method for validating a single epoch """

        self.model.model.eval()

        path2emb = {}
        for imgs, labels, img_paths in tqdm(self.val_loader):
            imgs = imgs.to(self.model.device)

            embs = self.model.model(imgs).to('cpu').detach().numpy()
            for img_path, emb in zip(img_paths, embs):
                path2emb[img_path] = emb

        y_trues, y_probs = [], []
        for idx, row in tqdm(self.easy_val_pairs.iterrows()):
            try:
                emb_1, emb_2 = path2emb[row.img_1], path2emb[row.img_2]
            except:
                continue
            sim = cosine_similarity(emb_1.reshape(1, -1), emb_2.reshape(1, -1))[0][0]

            y_trues.append(row.is_similar)
            y_probs.append(sim)

        y_trues = np.array(y_trues)
        y_probs = np.array(y_probs)

        metrics = self.calculate_metrics(y_trues=y_trues, y_probs=y_probs)

        print('Easy Val:')
        print(metrics)

        y_trues, y_probs = [], []
        for idx, row in tqdm(self.normal_val_pairs.iterrows()):
            try:
                emb_1, emb_2 = path2emb[row.img_1], path2emb[row.img_2]
            except:
                continue
            sim = cosine_similarity(emb_1.reshape(1, -1), emb_2.reshape(1, -1))[0][0]

            y_trues.append(row.is_similar)
            y_probs.append(sim)

        y_trues = np.array(y_trues)
        y_probs = np.array(y_probs)

        metrics_2 = self.calculate_metrics(y_trues=y_trues, y_probs=y_probs)

        print('Normal Val:')
        print(metrics_2)

        y_trues, y_probs = [], []
        for idx, row in tqdm(self.hard_val_pairs.iterrows()):
            try:
                emb_1, emb_2 = path2emb[row.img_1], path2emb[row.img_2]
            except:
                continue
            sim = cosine_similarity(emb_1.reshape(1, -1), emb_2.reshape(1, -1))[0][0]

            y_trues.append(row.is_similar)
            y_probs.append(sim)

        y_trues = np.array(y_trues)
        y_probs = np.array(y_probs)

        metrics_3 = self.calculate_metrics(y_trues=y_trues, y_probs=y_probs)

        print('Hard Val:')
        print(metrics_3)

        return metrics, metrics_2, metrics_3

    def save_model(self, epoch: int):
        """ Method for saving the model """

        model_path = os.path.join(self.model_config['model_save_path'], self.model_config['model_save_name'])
        if os.path.exists(model_path):
            torch.save(self.model.model, f"{model_path}/{epoch}.pth")
        else:
            os.mkdir(model_path)
            torch.save(self.model.model, f"{model_path}/{epoch}.pth")


    def save_results_log(self, epoch: int, train_loss: float, easy_roc_auc: float, normal_roc_auc: float,
                         hard_roc_auc: float):
        """ Method for logging model results """

        log_path = os.path.join(self.train_config['logs_save_path'], f"{self.model_config['model_save_name']}.txt")
        result = f"Epoch={epoch} Easy ROC_AUC={easy_roc_auc} Normal ROC_AUC={normal_roc_auc}  Hard ROC_AUC={hard_roc_auc} TrainLoss={train_loss}"

        with open(log_path, 'a') as f:
            f.write(result)
            f.write('\n')

    def train(self):
        """ Method for performing a model training cycle """
        for epoch in range(1, self.train_config['num_epochs']+1):

            train_loss = self.fit_epoch()
            easy_metrics, normal_metrics, hard_metrics = self.eval_epoch()

            self.save_model(epoch=epoch)

            self.save_results_log(epoch=epoch, train_loss=train_loss, easy_roc_auc=easy_metrics['roc_auc'],
                                  normal_roc_auc=normal_metrics['roc_auc'], hard_roc_auc=hard_metrics['roc_auc'])