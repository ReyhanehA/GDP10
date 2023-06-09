# coding: utf-8

from logging import getLogger

from scipy.sparse.construct import hstack
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import VectorizerMixin
from commonml.utils import get_nested_value

import numpy as np


logger = getLogger('commonml.text.custom_dict_vectorizer')


class CustomDictVectorizer(BaseEstimator, VectorizerMixin):

    def __init__(self, vect_rules):
        self.vect_rules = vect_rules
    
    def fit(self, raw_documents, y=None):
        for vect_rule in self.vect_rules:
            name = vect_rule.get('name')
            #logger.info(u'Fitting {0}'.format(name))
            vect = vect_rule.get('vectorizer')
            if not hasattr(vect, '__call__'):
                vect.fit(map(lambda x: get_nested_value(x, name, ''), raw_documents))

    def transform(self, raw_documents):
        results = []
        for vect_rule in self.vect_rules:
            name = vect_rule.get('name')
            #logger.info(u'Transforming {0}'.format(name))
            vect = vect_rule.get('vectorizer')
            if hasattr(vect, '__call__'):
                data = vect(map(lambda x: get_nested_value(x, name, ''), raw_documents))
            else:
                data = vect.transform(map(lambda x: get_nested_value(x, name, ''), raw_documents))
            results.append(data)
        return hstack(results, format='csr', dtype=np.float32)

    def fit_transform(self, raw_documents, y=None):
        results = []
        for vect_rule in self.vect_rules:
            name = vect_rule.get('name')
            #logger.info(u'Transforming {0}'.format(name))
            vect = vect_rule.get('vectorizer')
            if hasattr(vect, '__call__'):
                data = vect(map(lambda x: get_nested_value(x, name, ''), raw_documents))
            else:
                data = vect.fit_transform(map(lambda x: get_nested_value(x, name, ''), raw_documents))
            results.append(data)
        return hstack(results, format='csr', dtype=np.float32)

    def get_feature_names(self, append_name=True):
        results = []
        for vect_rule in self.vect_rules:
            vect = vect_rule.get('vectorizer')
            if append_name:
                name = vect_rule.get('name')
                names = map(lambda x: u'{0}={1}'.format(name, x), vect.get_feature_names())
            else:
                names = vect.get_feature_names()
            results.extend(names)
        return results

    def get_feature_size(self):
        size = 0
        for vect_rule in self.vect_rules:
            vect = vect_rule.get('vectorizer')
            size += len(vect.vocabulary_)
        return size

    def inverse_transform(self, X):
        names = np.array(self.get_feature_names())
        def get_names(x):
            indices = np.argwhere(x.toarray().flatten() > 0).flatten()
            if len(indices) == 0:
                return []
            else:
                return names[indices]
        return map(lambda x: get_names(x), X)

