# -*- coding: utf-8 -*-
"""Collection of methods used to generalize rules.
"""
import re
import copy
import nltk

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


def group_rules(rules, wordembedding):
    """Group rules that refer to same entity.

    Args:
        rules (list): List of tuples that contain question and answer.
        wordembedding (wordembedding.WordEmbedding): Word Embedding
            model.

    Returns:
        list: List with groups.
    """
    no_punctuation = [
        ' '.join(preprocessing.remove_punctation(
            nltk.word_tokenize(rule)
        )) for rule in rules
    ]
    no_stopwords = [
        preprocessing.remove_stopwords(rule) for rule in no_punctuation
    ]

    entities = list()
    for rule in no_stopwords:
        entity = ' '.join(find_keywords.find_entities(rule))
        if entity:
            entities.append(entity)
        else:
            # If there is no entities found append the rule itself
            entities.append(rule)
    lemmas = [lemmatizer.lemmatize(rule) for rule in entities]

    questions_keywords = list()
    for lemma in lemmas:
        words = re.split(r'[ \n/]', lemma)
        stemms = [stem(word) for word in words if word]
        words.extend(stemms)
        set_words = set(words)
        if '' in set_words:
            set_words.remove('')
        questions_keywords.append(set_words)
        # import pdb; pdb.set_trace()

    # Grouping only by similarity once similarity englobs common_words
    sents_group_common = list()
    for nosw in no_stopwords:
        words_nosw = set([
            w for w in nosw.split()
            if find_keywords.has_tag(w, 'N') or find_keywords.has_tag(w, 'NPROP')
        ])
        sents_group_common.append(words_nosw)

    groups_common = group_by_commom_words(sents_group_common)
    groups_similarity = group_by_similarity(questions_keywords, wordembedding)
    groups_similarity_cp = copy.deepcopy(groups_similarity)

    for i in range(len(groups_similarity_cp)):
        for j in range(len(groups_similarity_cp[i])):
            for k in range(len(groups_common)):
                if groups_similarity_cp[i][j] in groups_common[k]:
                    groups_similarity[i].extend(groups_common[k])

    groups_final = list()
    groups = [list(set(w)) for w in groups_similarity]
    while groups:
        group = groups.pop(0)
        if group not in groups_final:
            groups_final.append(group)

    return groups_final


def get_group_rejoinders(rules_ids, rules):
    """This method do create rejoinders for rules group.

    Args:
        rules_ids (list): List of rules indexes for the group.
        rules (list): List of rules.

    Returns:
        str: Text ChatScript rejoinder.
    """
    rejoinders = list()
    words_total = list()
    for index in rules_ids:
        # Store intentions to add futher
        intentions = re.findall(r'\[.*?\]', rules[index])
        words = re.sub(r'\*~\d+', '', rules[index])
        words = ' '.join(re.sub(r'\[.*?\]', 'INTENTIONS/V', words).split())

        # Removes auxiliary verbs
        tagged = find_keywords.tag_text(words)
        no_aux_verbs = re.sub(r'(\w+/V )(\w+/V)', r'\2', tagged)
        no_tags = re.sub(r'/\w+', '', no_aux_verbs)
        words = no_tags

        # Add stored intentions
        for intention in intentions:
            words = words.replace('INTENTIONS', intention[1:-1])

        # Mount rejoinder
        words = ' '.join(words.split())
        rejoinder = '\ta: ([{}]) \n\t\t^reuse(U{})'.format(words, index+1)
        rejoinders.append(rejoinder)
        words_total.append(words)

    return rejoinders, words_total


def generalize(question_rules, question_original, wordembedding):
    """Generalize the rules.

    Args:
        question_rules (list): List of question formated as CS rules.
        question_original (list): List of original questions in natural
            language.
        wordembedding (wordembedding.WordEmbedding): Word Embedding
            model.

    Yield:
        str: Rule generalized.
    """
    generalized_rules = list()
    questions_lower = [rule.lower() for rule in question_original]
    groups = group_rules(questions_lower, wordembedding)

    for index, group in enumerate(groups):
        group_rejoinders, words = get_group_rejoinders(group, question_rules)
        rejoinders = '\n'.join(group_rejoinders)
        questions = [question_original[qid] for qid in group]

        gen_rule = (
            'u: G{index} ([{words}])\n\t'
            'Aqui estão alguma opções relacionadas:\n\t - {questions}\n'
            '{group_rejoinders}'
        ).format(
            index=(index+1),
            words=' '.join(words),
            questions='\n\t - '.join(questions),
            group_rejoinders=rejoinders
        )
        generalized_rules.append(gen_rule)

    return '\n'.join(generalized_rules)
