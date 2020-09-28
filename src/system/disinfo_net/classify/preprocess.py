import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline, FeatureUnion, Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold


class ColumnSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

        
    def fit(self, X, y=None):
        return self

    
    def transform(self, X):
        assert isinstance(X, pd.DataFrame)

        try:
            return X[self.columns]
        except KeyError:
            cols_error = list(set(self.columns) - set(X.columns))
            raise KeyError('The DataFrame does not include the columns: %s' % cols_error)


class TypeSelector(BaseEstimator, TransformerMixin):
    def __init__(self, dtype):
        self.dtype = dtype

        
    def fit(self, X, y=None):
        return self

    
    def transform(self, X):
        assert isinstance(X, pd.DataFrame)
        selection = X.select_dtypes(include=[self.dtype])
        selection = selection.reindex(sorted(selection.columns), axis=1)
        return selection        
    

class CategoryTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, categorical_features):
        self.categorical_features = categorical_features

        
    def fit(self, X, y=None):
        return self

    
    def transform(self, X):
        # Fix up categorical datatypes that were downcasted
        X[self.categorical_features] = X[self.categorical_features].astype("category")
        return X


class ImportanceModelPreprocessor (BaseEstimator, TransformerMixin):
    def __init__(self, X):
        # Set up the numerical feature pipeline
        self.numerical_columns = X.select_dtypes(include=[np.number]).columns
        self.numerical_pipeline = make_numerical_pipeline(X)

        # Set up the categorical feature pipeline
        self.categorical_columns = sorted(X.select_dtypes(include=["object"]).columns)
        self.categorical_pipeline, self.onehot_encoder = make_categorical_pipeline(X, self.categorical_columns)

        # Set up the boolean feature pipeline
        self.boolean_columns = X.select_dtypes(include=["bool"]).columns
        self.boolean_pipeline = make_boolean_pipeline(X)

        
    def fit(self, X, y=None):
        self.numerical_pipeline.fit(X)
        self.categorical_pipeline.fit(X)
        self.boolean_pipeline.fit(X)
        return self

    
    def transform(self, X):
        # Transform the numerical features
        numerical_transformed = self.numerical_pipeline.transform(X)
        numerical_columns = X.select_dtypes(include=[np.number]).columns
        X_numerical = pd.DataFrame(data=numerical_transformed,
                                   columns=numerical_columns,
                                   index=X.index)

        # Transform the categorical features
        categorical_transformed = self.categorical_pipeline.transform(X)
        categorical_columns = self.onehot_encoder.get_feature_names(input_features=self.categorical_columns)
        X_categorical = pd.DataFrame(data=categorical_transformed,
                                     columns=categorical_columns,
                                     index=X.index)

        # Transform the boolean features
        boolean_transformed = self.boolean_pipeline.transform(X)
        boolean_columns = X.select_dtypes(include=["bool"]).columns
        X_boolean = pd.DataFrame(data=boolean_transformed,
                                 columns=boolean_columns,
                                 index=X.index)
        df = pd.concat([X_numerical, X_boolean, X_categorical], axis=1)
        return df


def make_numerical_pipeline (X):
    pipeline = make_pipeline(
        ColumnSelector(X.columns),
        TypeSelector(np.number),
        SimpleImputer(strategy="median"),
        StandardScaler()
    )
    return pipeline


def make_categorical_pipeline (X, categorical_features):
    onehot_encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
    pipeline = make_pipeline(
        ColumnSelector(X.columns),
        CategoryTransformer(categorical_features=categorical_features),
        TypeSelector("category"),
        SimpleImputer(strategy="most_frequent"),
        onehot_encoder
    )
    return pipeline, onehot_encoder


def make_boolean_pipeline (X):
    pipeline = make_pipeline(
        ColumnSelector(X.columns),
        TypeSelector("bool")
    )
    return pipeline


def make_complete_preprocessor (numeric=True, categorical=True, boolean=True):
    transformer_list = []
    if numeric:
        numeric_pipeline = ("numeric_features",
                            make_pipeline(
                                TypeSelector(np.number),
                                SimpleImputer(strategy="median"),
                                StandardScaler()
                            ))
        transformer_list.append(numeric_pipeline)

    if categorical:
        categorical_pipeline = ("categorical_features",
                                make_pipeline(
                                    TypeSelector("category"),
                                    SimpleImputer(strategy="most_frequent"),
                                    OneHotEncoder(sparse=False, handle_unknown="ignore")
                                ))
        transformer_list.append(categorical_pipeline)

    if boolean:
        boolean_pipeline = ("boolean_features",
                            make_pipeline(
                                TypeSelector("bool")
                            ))
        transformer_list.append(boolean_pipeline)
    
    preprocess_pipeline = make_pipeline(
        FeatureUnion(transformer_list=transformer_list)
    )
    return preprocess_pipeline
