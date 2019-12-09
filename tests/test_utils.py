# -*- coding: utf-8 -*-
from utils import lemmatizer
from utils import plural_singular

class TestUtils(object):

    def test_plural_singular(self):
        assert 'pedidos' == plural_singular.get_plurals('pedido')

    def test_lemmatize(self):
        expected = 'testando/testar a/o flexão/flexão das/do palavras/palavra'
        result = lemmatizer.lemmatize('testando a flexão das palavras')

        assert result.strip() == expected.strip()


