# -*- coding: utf-8 -*-
import wordembedding
import generalize_rules

class TestGeneralizeRules(object):
    cbow = wordembedding.CBoW()

    def test_group_by_similarity(self):
        groups = [
            {'arroz', 'cachorro', 'feijão', 'montanha'},
            {'bicicleta', 'cão'},
            {'cadeira', 'w'},
            {'parque', 'cachorrinho', 'comprar'},
        ]
        result = generalize_rules.group_by_similarity(groups, self.cbow)
        assert result == [[0, 1, 3], [2]]

    def test_group_by_commom_words(self):
        groups = [
            {'a', 's', 'd'},
            {'z', 's', 'c'},
            {'q', 'w', 'e'},
            {'t', 's', 'y'},
        ]
        result = generalize_rules.group_by_commom_words(groups)
        assert result == [[0, 1, 3], [2]]

    def test_group_rules(self):
        rules = [
            'localizo *~1 código *~2 vale_trocas',
            'funciona *~1 postagem',
            'quero postar *~1 produto',
        ]
        expected = [[1, 2], [0]]
        result = generalize_rules.group_rules(rules, self.cbow)
        assert result == expected
