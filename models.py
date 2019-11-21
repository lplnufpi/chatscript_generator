# -*- coding: utf-8 -*-
import re

import add_syns
import preprocessing
import find_keywords
import generalize_rules


class Rule(object):
    label_type = None
    rule_id = None
    title = None
    original_question = None
    nosw_question = None
    ppcd_question = None
    add_syns_question = None
    final_question = None
    answer = None
    ctx_entities = None

    label = None
    entities = None
    intentions = None
    intentions_syns_dict = None
    rejoinders = None

    def __init__(
        self, rule_id, title, question,
        answer, ctx_entities, embedding_model, label_type='U'
    ):
        self.label_type = label_type
        self.rule_id = rule_id
        self.title = title
        self.original_question = question
        self.answer = answer
        self.ctx_entities = ctx_entities

        self.do_preprocessing()
        self.find_intentions_entities()
        self.add_syns(embedding_model)
        self.label = label_type + str(rule_id)

    def do_preprocessing(self):
        self.ppcd_question = preprocessing.preprocess(
            self.original_question, self.ctx_entities
        )

    def find_intentions_entities(self):
        # Remove wildcards from preprocessed question
        self.nosw_question = re.sub(r'\*~\d+', '', self.ppcd_question)

        self.entities = find_keywords.find_entities(self.nosw_question)
        self.intentions = find_keywords.find_intention(
            self.nosw_question, self.entities
        )

    def add_syns(self, embedding_model):
        self.intentions_syns_dict = add_syns.get_syns(
            self.intentions, embedding_model
        )
        self.add_syns_question = add_syns.add_intentions_syns(
            self.ppcd_question, self.intentions_syns_dict
        )

    @property
    def intentions_syns_list(self):
        intentions = list()
        for _, value in self.intentions_syns_dict.items():
            intentions.extend(value)
        return intentions

    @property
    def keywords(self):
        kw = set(
            self.intentions +
            self.intentions_syns_list +
            self.entities
        )
        return list(kw)

    def __str__(self):
        text = (
            'u: {label_type}{id} ({rule})\n\t{answer}'
        ).format(
            label_type=self.label_type,
            id=self.rule_id,
            rule=self.add_syns_question,
            answer=self.answer
        )
        return text


class Topic(object):
    name = None
    keywords = list()
    rules = None
    generalized_rules = list()

    def __init__(self, name, rules):
        self.name = name
        self.rules = rules
        for rule in self.rules:
            self.keywords.extend(rule.keywords)

    def generalize_rules(self, wordembedding):
        self.generalized_rules = generalize_rules.generalize(
            self.rules, wordembedding
        )

    def __str__(self):
        top_header = u'topic: ~{} keep repeat ({})\n\n'.format(
            self.name, ' '.join(set(self.keywords))
        )

        rules_text = '\n\n'.join([rule.__str__() for rule in self.rules])
        gen_rules_text = '\n\n'.join(
            [rule.__str__() for rule in self.generalized_rules]
        )

        return top_header + rules_text + '\n\n\n' + gen_rules_text
