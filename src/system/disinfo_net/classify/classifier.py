#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from disinfo_net.classify.feature_extractor import FeatureExtractor
from disinfo_net.classify.preprocess import ImportanceModelPreprocessor, make_complete_preprocessor
from disinfo_net.postgres.pg import DisinfoRawDataDB

class DisinformationClassifier:

    def __init__(self, raw_training_data, desired_features, save_ft_names=False):
        self.desired_features = desired_features
        self.X, self.y = self.extract_training_data(raw_training_data, desired_features)

        if save_ft_names:
            self.preprocessor = ImportanceModelPreprocessor(self.X)
        else:
            self.preprocessor = make_complete_preprocessor(numeric=True, 
                                                           categorical=True,
                                                           boolean=True)

        self.classifier = RandomForestClassifier(n_estimators=100,
                                                 class_weight="balanced",
                                                 random_state=0)

    def extract_training_data(self, raw_training_data, desired_features):
        extracted_training_data = []
        for resp in raw_training_data:
            domain = resp.domain
            target = resp.target
            features = FeatureExtractor.get_features(resp, desired_features)
            extracted_training_data.append((features, target))

        # Create X and y
        all_features = [tup[0] for tup in extracted_training_data]
        all_targets = [tup[1] for tup in extracted_training_data]

        X = pd.concat(all_features)
        y = all_targets

        # Return X and y
        return X, y

    @staticmethod
    def load_model_from_file(filename):
        with open(filename, "rb") as f:
            m = pickle.load(f)
        return m

    def save(self, filename):
        # Save this model to disk
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def preprocess(self, X, isTrainingData):
         # Cast object columns to category
        categorical_features = X.select_dtypes("object").columns
        X[categorical_features] = X[categorical_features].astype("category")
        if isTrainingData:
            self.preprocessor.fit(X)
        X = self.preprocessor.transform(X)
        return X

    def train(self):
        # Preprocess training data
        self.X = self.preprocess(self.X, True)

        # Fit the classifier on the training data
        self.classifier.fit(self.X, self.y)

    def predict(self, resp):
        try:
            # Get features from raw data
            X_new = FeatureExtractor.get_features(resp, self.desired_features)

            # Preprocess features
            X_new = self.preprocess(X_new, False)

            # Make a prediction
            targets = self.classifier.classes_
            probas = self.classifier.predict_proba(X_new)[0].tolist()
            probas_dict = {targets[0]: probas[0], targets[1]: probas[1], targets[2]: probas[2]}
            y_new = max(probas_dict, key=probas_dict.get)
            return (y_new, probas_dict)
        except Exception as e:
            print(e)
            return "unclassified", None
