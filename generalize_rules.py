# -*- coding: utf-8 -*-
"""Collection of methods used to generalize rules.
"""
import re
import copy
import nltk

import models
import preprocessing
import find_keywords
from utils import lemmatizer


def stem(word):
    """This methods use RSLPStemmer to stem words.

    Args:
        word (str): Text to stem.

    Return:
        str: Stemmed text.
    """
    stemmer = nltk.stem.RSLPStemmer()
    if word:
        return stemmer.stem(word)
    return word


def group_by_commom_words(sents):
    """Method used to group by common words.

    Example:
        >>> sents = [{'a', 'b'}, {'z', 'b'}, {'t', 'y'}]
        >>> group_by_commom_words(sents)
        [[0, 1], [2]]

    Args:
        sents (list): List of sets with words.

    Returns:
        list: List of groups.
    """
    common_words = list()
    for i in range(len(sents)):
        for j in range(len(sents)):
            if i != j and sents[i] & sents[j]:

                tam = len(common_words)
                if tam == 0:
                    common_words.append([i, j])
                else:
                    for g in range(tam):
                        if i in common_words[g] or j in common_words[g]:
                            common_words[g].extend([i, j])
                            break
                    else:
                        common_words.append([i, j])

    common_words = [list(set(cw)) for cw in common_words]
    common_words_flatten = list()
    for cw in common_words:
        common_words_flatten.extend(cw)

    non_commom = [
        [i] for i in range(len(sents)) if i not in common_words_flatten
    ]
    return common_words + non_commom


def group_by_similarity(sents, wordembedding):
    """Method used to group by similarity words.

    Example:
        >>> sents = [{'a', 'b'}, {'z', 'b'}, {'t', 'y'}]
        >>> group_by_similarity(sents)
        [[0, 1], [2]]

    Args:
        sents (list): List of sets with words.

    Returns:
        list: List of groups.
    """
    similarity = wordembedding.ideal_similarity
    common_words = list()
    for i in range(len(sents)):
        for j in range(len(sents)):
            if i != j:
                for word_i in sents[i]:
                    for word_j in sents[j]:
                        try:
                            sim = wordembedding.model.similarity(word_i, word_j)
                        except KeyError:
                            sim = similarity + 1 if word_i == word_j else 0


                        if sim < similarity:
                            continue
                        if sim < 1:
                            text = 'Similarity {}:{} -> {}'.format(
                                word_i, word_j, sim)
                            print(text)
                        tam = len(common_words)
                        if tam == 0:
                            common_words.append([i, j])
                        else:
                            for g in range(tam):
                                if i in common_words[g] or j in common_words[g]:
                                    common_words[g].extend([i, j])
                                    break
                            else:
                                common_words.append([i, j])

    common_words = [list(set(cw)) for cw in common_words]
    common_words_flatten = list()
    for cw in common_words:
        common_words_flatten.extend(cw)

    non_commom = [
        [i] for i in range(len(sents)) if i not in common_words_flatten
    ]
    return common_words + non_commom


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


def group_by_entities(rules):
    entities = get_all_entities(rules)
    common_entities = get_rules_common_entities(entities)
    groups = list()
    keywords = list()

    for rule in rules:
        keywords.extend(
            [ent for ent in set(entities) if ent not in common_entities]
        )

    added_rules = list()
    for keyword in set(keywords):
        rules_group = list()
        for rule in rules:
            for entity in rule.entities:
                if re.search(keyword, entity) or re.search(keyword[:-1], entity):
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


def group_rules(rules, wordembedding):
    """Group rules that refer to same entity.

    Args:
        rules (list): List of tuples that contain question and answer.
        wordembedding (wordembedding.WordEmbedding): Word Embedding
            model.

    Returns:
        list: List with groups.
    """

    entities = list()
    for rule in rules:
        if rule.entities:
            entities.append(' '.join(rule.entities))
        else:
            entities.append(rule.nosw_question)

    entities_words = list()
    for ent in entities:
        entities_words.extend(ent.split())

    freqdist = nltk.FreqDist(entities_words)
    common_words = [word for word, dist in freqdist.most_common() if dist > 2]
    entities_no_common = list()
    for entity in entities:
        ent = entity
        for word in common_words:
            ent = ent.replace(word, '')
        entities_no_common.append(ent)

    lemmas = [lemmatizer.lemmatize(entity) for entity in entities_no_common]
    # Obtains every question keywords added with it's lemmas and stems
    questions_keywords = list()
    for lemma in lemmas:
        words = re.split(r'[ \n/]', lemma)
        stemms = [stem(word) for word in words if word]
        words.extend(stemms)
        set_words = set(words)
        if '' in set_words:
            set_words.remove('')
        questions_keywords.append(set_words)

    # Grouping only by similarity once similarity englobs common_words
    groups_similarity = group_by_similarity(questions_keywords, wordembedding)
    rules_groups = list()
    for group in groups_similarity:
        rules_group = list()
        for rule_id in group:
            rules_group.append(
                [rule for rule in rules if rule.rule_id == rule_id][0]
            )
        rules_groups.append(rules_group)

    return rules_groups


def get_rejoinder_pattern(rule):
    """This method creates the rejoinder match pattern.

    Args:
        rule (str): Chatscript rule.
    """
    # Store intentions to add futher
    intentions = re.findall(r'\[.*?\]', rule)
    pattern = re.sub(r'\*~\d+', '', rule)
    pattern = ' '.join(re.sub(r'\[.*?\]', 'INTENTIONS/V', pattern).split())

    # Removes auxiliary verbs
    tagged = find_keywords.tag_text(pattern)
    no_aux_verbs = re.sub(r'(\w+/V )(\w+/V)', r'\2', tagged)
    no_tags = re.sub(r'/\w+', '', no_aux_verbs)
    pattern = no_tags

    # Add stored intentions
    for intention in intentions:
        pattern = pattern.replace('INTENTIONS', intention[1:-1])
    pattern = ' '.join(set(pattern.split()))
    return pattern


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
    groups = group_by_entities(topic.rules)

    for index, group in enumerate(groups):
        gen_rule = models.GenericRule(
            index, group.rules, group.entity, topic.name
        )
        generalized_rules.append(gen_rule)

    return generalized_rules
