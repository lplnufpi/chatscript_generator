# -*- coding: utf-8 -*-
"""Collection of methods used to generalize rules.
"""
import re
import nltk

import models


def get_all_entities(rules):
    all_entities = list()

    entities = list()
    for rule in rules:
        entities.extend(rule.entities)

    for ent in entities:
        all_entities.extend(ent.split())

    return all_entities


def get_rules_common_entities(entities):
    freqdist = nltk.FreqDist(entities)
    common_words = [word for word, dist in freqdist.most_common() if dist > 2]
    return set(common_words)


def print_group(groups):
    for key, rules in groups.items():
        text = [rule.original_question for rule in rules]
        print('{}: [{}]'.format(key, text))


def get_keywords(rules):
    entities = get_all_entities(rules)
    common_entities = get_rules_common_entities(entities)
    keywords = list()

    for rule in rules:
        keywords.extend(
            [ent for ent in set(entities) if ent not in common_entities]
        )
    return keywords


def group_by_entities(rules, keywords):
    groups = list()

    added_rules = list()
    for keyword in keywords:
        rules_group = list()
        for rule in rules:
            for entity in rule.entities:
                if (
                    re.search(keyword, entity) or
                    re.search(keyword[:-1], entity)
                ):
                    rules_group.append(rule)
                    break

        # Verify added rules to unite groups with same rules
        if rules_group not in added_rules:
            added_rules.append(rules_group)
            groups.append(models.Group(rules_group, keyword))
        else:
            for group in groups:
                if group.rules == rules_group:
                    group.entity = group.entity + ' ' + keyword

    return groups


def get_singular_or_plural(word, keywords):
    if word+'s' in keywords:
        return word+'s'
    elif word.endswith('s'):
        return word[:-1]
    return None


def get_entity_pattern(entity, keywords):

    entity_parts = entity.split()

    if len(entity_parts) > 1:
        result = '"{}"'
    else:
        result = '{}'

    original = result.format(entity)
    plural = list()

    for part in entity_parts:
        sp = get_singular_or_plural(part, keywords)
        if sp:
            plural.append(sp)

    if plural:
        text_result = '[{}]'.format(
            original + ' ' + result.format(' '.join(plural))
        )
    else:
        text_result = original

    return text_result


def sort_by_entities(rules):
    result_rules = list()
    keywords = get_keywords(rules)
    all_entities = get_all_entities(rules)
    common_words = get_rules_common_entities(all_entities)

    sorted_rules = sorted(rules, key=lambda r: len(r.entities), reverse=True)
    for rule in sorted_rules:
        entities = [ent for ent in rule.entities if ent not in common_words]
        entities = sorted(
            entities,
            key=lambda ent: rule.nospace_question.index(ent) if ent in rule.nospace_question else 1000
        )
        pattern_entts = [get_entity_pattern(ent, keywords) for ent in entities]
        pattern = ' * '.join(pattern_entts)

        nrule = models.Rule(
            rule.rule_id, '', '',
            '^reuse(U{})'.format(rule.rule_id),
            None, None, label_type='S',
            add_syns_question=pattern
        )
        result_rules.append(nrule)
    return result_rules


def generalize(topic, wordembedding):
    """Generalize the rules.

    Args:
        question_rules (list): List of question formated as CS rules.
        question_original (list): List of original questions in natural
            language.
        wordembedding (wordembedding.WordEmbedding): Word Embedding
            model.
        rules_title (list): List of rules titles.

    Yield:
        str: Rule generalized.
    """
    generalized_rules = list()
    keywords = get_keywords(topic.rules)
    groups = group_by_entities(topic.rules, set(keywords))

    for index, group in enumerate(groups):
        gen_rule = models.GenericRule(
            index, group.rules, group.entity, topic.name
        )
        generalized_rules.append(gen_rule)

    return generalized_rules
