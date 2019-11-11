# -*- coding: utf-8 -*-
import wordembedding
import generalize_rules
import preprocessing


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
            'localizo código vale_trocas',
            'funciona postagem',
            'quero postar produto',
        ]
        expected = [[1, 2], [0]]
        result = generalize_rules.group_rules(rules, self.cbow)
        assert result == expected

    def test_group_rules_dois(self):
        rules = [
            'como localizo o código do meu vale trocas?',
            'como funciona a postagem?',
            'quero postar meu produto.',
            'a loja disponibiliza embalagem de presente?',
            'onde solicitar a montagem de bicicleta?',
            'posso utilizar o bike service para qualquer bicicleta?',
            'o que é bike service?',
            'o que é nota fiscal eletrônica?',
            'como faço para resgatar a segunda via da nota fiscal?',
        ]

        expected = [[1, 2], [4, 5, 6], [8, 7], [0], [3]]
        result = generalize_rules.group_rules(rules, self.cbow, similarity=0.9)
        assert result == expected
