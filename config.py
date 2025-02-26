import os
from datetime import datetime

from mltu.configs import BaseModelConfigs

class ModelConfigs(BaseModelConfigs):
    def __init__(self):
        super().__init__()
        self.trained_models = 'trained_model'
        self.root = 'data'
        self.height = 64
        self.width = 128
        self.max_label_len = 32
        self.epochs = 100        
        self.batch_size = 8
        self.learning_rate = 1e-3
        self.train_workers = 4
        self.logging = 'tensorboard'
        self.checkpoint = None
