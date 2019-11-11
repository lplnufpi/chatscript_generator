# -*- coding: utf-8 -*-
import re
import nltk

import preprocessing
from utils import lemmatizer


def stem(word):
    stemmer = nltk.stem.RSLPStemmer()
    if word:
        return stemmer.stem(word)


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


def group_by_similarity(sents, wordembedding, similarity=0.8):
    """Method used to group by similarity words.

    Example:
        >>> sents = [{'a', 'b'}, {'z', 'b'}, {'t', 'y'}]
        >>> group_by_commom_words(sents)
        [[0, 1], [2]]

    Args:
        sents (list): List of sets with words.
        similarity (float): Similarity score.

    Returns:
        list: List of groups.
    """
    common_words = list()
    for i in range(len(sents)):
        for j in range(len(sents)):
            if i != j:
                for word_i in sents[i]:
                    for word_j in sents[j]:
                        sim = wordembedding.model.similarity(word_i, word_j)
                        if sim >= similarity:
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


def group_rules(rules, cbow):
    """Group rules that refer to same entity.

    Args:
        rules (list): List of tuples that contain question and answer.

    Returns:
        dict: Dict where the keys are the.
    """
    wildcard = re.compile(r'\*~\d+')
    separators = re.compile(r'[ \n/]')
    no_wildcrd = [wildcard.sub('', rule) for rule in rules]
    no_stopwords = [preprocessing.remove_stopwords(rule) for rule in no_wildcrd]
    lemmas = [lemmatizer.lemmatize(rule) for rule in no_stopwords]

    questions_keywords = list()
    for lemma in lemmas:
        words = separators.split(lemma)
        stemms = [stem(word) for word in words if word]
        words.extend(stemms)
        set_words = set(words)
        set_words.remove('')
        questions_keywords.append(set_words)

    # USAR CBOW PARA SABER DISTÂNCIAS ENTRE PALAVRAS
    groups = group_by_commom_words(questions_keywords)
    # import pdb;pdb.set_trace()
    return groups


def get_group_rejoinders(rules_ids, rules):
    rejoinders = list()
    for _id in rules_ids:
        words = ''
        rejoinder = 'a: (<<{}>>) ^reuse(U{})'.format(words, _id)
        rejoinders.append(rejoinder)

    return rejoinders


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
    groups = group_rules(question_rules, wordembedding)
    question_original = '\n'.join(question_original)
    for index in range(len(groups)):
        group_rejoinders = get_group_rejoinders(groups[index], question_rules)
        rejoinders = '\n'.join(group_rejoinders)

        gen_rule = (
            'u: G{index} ([{words}])'
            'Aqui estão alguma opções relacionadas:\n{questions}\n'
            '{group_rejoinders}'
        ).format(
            index=(index+1),
            # words=entities,
            questions=question_original,
            group_rejoinders=rejoinders
        )

    return generalized_rules
