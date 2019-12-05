# -*- coding: utf-8 -*-
import re

import add_syns
import preprocessing
import find_keywords


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
            pattern = '[~yess ~adv_afirmacao]'
            cant_help = (
                '\n\ta: ([~noo ~adv_negacao])\n\t'
                '   $err = ^save_input_error($quest %topic)\n\t'
                '   ^pick(~cant_help), ^pick(~not_ready_yet), mas '
                '^pick(~tranfeer)'
            )

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
    _entities_singular = None

    def __init__(
        self, rule_id, title, question, answer, ctx_entities,
        embedding_model, label_type='U', add_syns_question=None
    ):
        self.label_type = label_type
        self.rule_id = rule_id
        self.title = title
        self.original_question = question
        self.answer = answer
        self.ctx_entities = ctx_entities
        self.label = label_type + str(rule_id)

        if add_syns_question is None:
            self.do_preprocessing()
            self.find_intentions_entities()
            self.add_syns(embedding_model)
            self._entities_singular = list()
        else:
            self.add_syns_question = add_syns_question

    def do_preprocessing(self):
        self.ppcd_question = preprocessing.preprocess(
            self.original_question, self.ctx_entities
        )

    def find_intentions_entities(self):
        # Remove wildcards from preprocessed question
        self.nosw_question = re.sub(r'\*~\d+', '', self.ppcd_question)

        self.entities = find_keywords.find_entities(self.nosw_question)

        self.splited_entities = list()
        for ent in self.entities:
            self.splited_entities.extend(ent.split())
        self.splited_entities = set(self.splited_entities)

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
    def nospace_question(self):
        return self.nosw_question.replace('  ', ' ')

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
        call_review = '\n\t$rule = %rule\n\t REVIEW ^reuse(~review_interacion.REVIEW)'
        text = (
            '{extra_space}u: {label} ({rule}){space}{answer}{call_review}'
        ).format(
            extra_space='\n'*2 if self.rule_id == 0 else '',
            label=self.label,
            id=self.rule_id,
            rule=self.add_syns_question,
            space='\n\t' if self.label_type != 'S' else ' ',
            answer=self.answer,
            call_review=call_review
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
    original_topic_name = None

    def __init__(
        self, rule_id, group, words, original_topic_name, label_type='G'
    ):
        self.rule_id = rule_id
        self.label_type = label_type
        self.label = label_type + str(rule_id)
        self.group = group
        self.questions = [rule.original_question for rule in group]
        self.words = words
        self.original_topic_name = original_topic_name
        self.generate_rejoinders()

    def generate_rejoinders(self):
        self.rejoinders = list()
        if len(self.group) > 1:
            all_words = set()
            group_entities = self.words.split()
            for rule in self.group:
                # Remove common questions keywords to improve distinction
                keywords = [
                    kw for kw in rule.keywords
                    if kw not in group_entities and kw not in all_words
                ]
                all_words.update(keywords)
                keywords = ' '.join(keywords)
                label = '~{}.{}'.format(self.original_topic_name, rule.label)
                rej = Rejoinder(label, keywords)
                self.rejoinders.append(rej)
            # Do remove repeated words in multiple rejoinders
        else:
            keywords = None
            label = '~{}.{}'.format(
                self.original_topic_name, self.group[0].label
            )
            rej = Rejoinder(label, keywords)
            self.rejoinders.append(rej)

    def rejoinders_text(self):
        return '\n'.join([ref.__str__() for ref in self.rejoinders])

    def __str__(self):
        if len(self.group) > 1:
            gen_rule = (
                'u: {label} (<<{words}>>)\n\t'
                '$quest = %originalsentence\n\t'
                '^pick(~not_well_understood), %user, '
                'mas ^pick(~search_options):\n\t - {questions}\n'
                '{group_rejoinders}'
            ).format(
                label=self.label,
                words=self.words,
                questions='\n\t - '.join(self.questions) + ' -',
                group_rejoinders=self.rejoinders_text()
            )
        else:
            gen_rule = (
                'u: {label} (<<{words}>>)\n\t'
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


class Group(object):
    rules = None
    entity = None

    def __init__(self, rules, entity):
        self.rules = rules
        self.entity = entity


class Topic(object):
    name = None
    keywords = None
    rules = None
    max_return_code = 100
    beauty_name = None

    def __init__(self, name, rules, beauty_name=None):
        self.name = name
        self.rules = rules
        self.keywords = list()
        self.beauty_name = beauty_name

        if self.name.endswith('_gen'):
            self.keywords.append('REGRAS_GENERICAS')
            self.random = ''
        else:
            self.random = ''
            for rule in self.rules:
                if rule.entities:
                    self.keywords.extend(rule.entities)
                else:
                    self.keywords.append(rule.original_question)

    def __str__(self):
        top_header = (
            u'topic: ~{name} keep repeat {random}({keywords})\n'
        ).format(
            name=self.name,
            random=self.random,
            keywords=' '.join(set(self.keywords))
        )

        rules_text = '\n'.join([rule.__str__() for rule in self.rules])
        if self.name.endswith('_gen'):
            search_rule_text = ''
        else:
            search_rule_text = (
                'u: SEARCH_RULE ()\n'
                '\t$res = ^search_rule(%originalsentence %topic) / 256\n'
                '\tif($res<{max_return}){{\n'
                '\t\t^reuse(^join(U $res))\n'
                '\t}}else{{\n'
                '\t\t^respond(~{name})\n'
                '\t}}\n'
            ).format(name=self.name+'_gen', max_return=self.max_return_code)

        return top_header + rules_text + '\n\n\n' + search_rule_text
