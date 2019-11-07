# -*- coding: utf-8 -*-
"""Module for test
"""
import topics
import wordembedding


class Test(object):
    cbow = wordembedding.CBoW()

    def test_get_topic_keywords(self):
        result = topics.get_topic_keywords(
            [
                (
                    '*~1 loja (disponibiliza|oferece) embalagem',
                    'oferecemos empacotamento grátis para você'
                ),
                (
                    '(utilizar|usar) *~1 bicicleta',
                    'utilize nossas bicicletas à vontade'
                )
            ]
        )
        expected = {
            'empacotamento grátis', 'loja', 'embalagem', 'bicicleta',
            'bicicletas'
        }
        assert result == expected