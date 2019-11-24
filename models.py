# -*- coding: utf-8 -*-
import re
import copy

import add_syns
import preprocessing
import find_keywords
import generalize_rules


class Rejoinder(object):
    rule_label = None
    pattern = None

    def __init__(self, rule_label, pattern=None):
        self.rule_label = rule_label
        self.pattern = pattern

    def __str__(self):
        if self.pattern:
            pattern = '[{}]'.format(self.pattern)
            cant_help = ''
        else:
            pattern = '~yess'
            cant_help = '\n\ta: (~noo) Não posso lhe ajudar'

        string = (
            '\ta: ({pattern})\n\t'
            '   $res = ^save_input($quest %topic {rule_label})\n\t'
            '   ^reuse({rule_label})'
            '{cant_help}'
        ).format(
            pattern=pattern, rule_label=self.rule_label, cant_help=cant_help
        )

        return string


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
            'u: {label} ({rule})\n\t{answer}'
        ).format(
            label=self.label,
            id=self.rule_id,
            rule=self.add_syns_question,
            answer=self.answer
        )
        return text


class GenericRule(object):
    group = None
    words = None
    questions = None
    rule_id = None
    label = None
    label_type = None
    rejoinders = None

    def __init__(self, rule_id, group, label_type='G'):
        self.rule_id = rule_id
        self.label_type = label_type
        self.label = label_type + str(rule_id)
        self.group = group
        words = list()
        for rule in group:
            words.extend(rule.keywords)

        self.words = ' '.join(set(words))
        self.questions = [rule.original_question for rule in group]
        self.generate_rejoinders()

    def generate_rejoinders(self):
        self.rejoinders = list()
        if len(self.group) > 1:
            for rule in self.group:
                keywords = ' '.join(rule.keywords)
                rej = Rejoinder(rule.label, keywords)
                self.rejoinders.append(rej)
        else:
            rej = Rejoinder(self.group[0].label)
            self.rejoinders.append(rej)

    def rejoinders_text(self):
        return '\n'.join([ref.__str__() for ref in self.rejoinders])

    def __str__(self):
        if len(self.group) > 1:
            gen_rule = (
                'u: {label} ([{words}])\n\t'
                '$quest = %originalsentence\n\t'
                '^pick(~not_well_understood), %user, '
                'mas ^pick(~search_options):\n\t - {questions}\n'
                '{group_rejoinders}'
            ).format(
                label=self.label,
                words=self.words,
                questions='\n\t - '.join(self.questions),
                group_rejoinders=self.rejoinders_text()
            )
        else:
            gen_rule = (
                'u: {label} ([{words}])\n\t'
                '$quest = %originalsentence\n\t'
                '^pick(~not_well_understood), %user, '
                '^pick(~you_mean) "{sugestion}"?\n'
                '{group_rejoinders}'
            ).format(
                label=self.label,
                words=self.words,
                sugestion=self.group[0].title,
                group_rejoinders=self.rejoinders_text()
            )

        return gen_rule


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

        rules_text = '\n'.join([rule.__str__() for rule in self.rules])
        gen_rules_text = '\n'.join(
            [rule.__str__() for rule in self.generalized_rules]
        )

        return top_header + rules_text + '\n\n\n' + gen_rules_text
