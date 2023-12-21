import os
import urllib.request as request
from zipfile import ZipFile
from pathlib import Path
from src.cnnClassifier import logger
import tensorflow as tf
from src.cnnClassifier.entity.config_entity import (DataIngestionConfig, PrepareBaseModelConfig)


class PrepareBaseModel:
    def __init__(self, config: PrepareBaseModelConfig ):
        self.config = config


    def get_base_model(self):
        self.model = tf.keras.applications.vgg16.VGG16(
           include_top = self.config.params_include_top,
            weights = self.config.params_weights,
           input_shape =  self.config.params_image_size
        )
        
        self.save_model(path=self.config.base_model_path,
                        model= self.model)

    @staticmethod   
    def save_model(path: Path,
                   model: tf.keras.Model):
        model.save(path)


    @staticmethod
    def prepare_full_model(model,
                        classes,
                        freeze_all,
                        freeze_till,
                        learning_rate):
        
        if freeze_all:
            for layer in model.layers:
                model.trainable = False
        elif (freeze_till is not None) and (freeze_till > 0):
            for layer in model.layers[:-freeze_till]:
                model.trainable = False

        flatten_in = tf.keras.layers.Flatten()(model.output)
        predection = tf.keras.layers.Dense(
            units=classes,
            activation="softmax"
        )(flatten_in)

        full_model = tf.keras.models.Model(
            inputs = model.input,
            outputs= predection
        )

        full_model.compile(
            optimizer= tf.keras.optimizers.SGD(learning_rate=learning_rate),
            loss= tf.keras.losses.CategoricalCrossentropy(),
            metrics=['accuracy']
        )

        full_model.summary()
        return full_model
    

    def updated_base_model(self):
        self.full_model = self.prepare_full_model(
            model=self.model,
            classes=self.config.params_classes,
            freeze_all=True,
            freeze_till=None,
            learning_rate=self.config.params_learning_rate
        )
        self.save_model(path=self.config.updated_base_model_path,
                        model=self.full_model)
    