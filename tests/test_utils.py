# -*- coding: utf-8 -*-
from utils import lemmatizer

class TestUtils(object):

    def test_lemmatize(self):
        expected = 'testando/testar a/o flexão/flexão das/do palavras/palavra'
        result = lemmatizer.lemmatize('testando a flexão das palavras')

        assert result.strip() == expected.strip()
