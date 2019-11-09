# -*- coding: utf-8 -*-
import preprocessing

class Test(object):

    def test_remove_punctation(self):
        result = preprocessing.remove_punctation(
            ['olá', ',', 'como', 'vai', '?']
        )
        expected = ['olá', 'como', 'vai']
        assert result == expected

    def test_replace_stopwords(self):
        result = preprocessing.replace_stopwords(['texto', 'com', 'stopword'])
        expected = ['texto', preprocessing.WILDCARD, 'stopword']
        assert result == expected

    def test_add_wildcards(self):
        wd = preprocessing.WILDCARD
        wd2 = preprocessing.WILDCARD_MASK.format(
            preprocessing.WILDCARD_DEFAULT_VALUE*2
        )
        wd7 = preprocessing.WILDCARD_MASK.format(
            preprocessing.WILDCARD_DEFAULT_VALUE*7
        )

        result = preprocessing.add_wildcards(
            'texto {} {} mais texto {} {} {} {}'.format(
                wd, wd, wd, wd2, wd2, wd2
            )
        )
        expected = 'texto {} mais texto {}'.format(wd2, wd7)
        assert result == expected

    def test_replace_context_entities(self):
        ctx_entities = ['minha conta', 'nome empresa']
        result = preprocessing.replace_context_entities(
            ctx_entities, 'acessar minha conta na nome empresa'
        )
        expected = 'acessar minha_conta na nome_empresa'
        assert result == expected

    def test_strip_wildcards(self):
        text = '*~1 *~1 fulano *~1 fulano *~1 *~1'
        expected = 'fulano *~1 fulano'
        result = preprocessing.strip_wildcards(text)
        assert result == expected

    def test_preprocess(self):
        ctx_entities = ['minha conta']
        result = preprocessing.preprocess(
            'Gostaria de saber como acessar minha conta',
            ctx_entities
        )
        expected = 'gostaria *~1 saber *~1 acessar minha_conta'
        assert result == expected
