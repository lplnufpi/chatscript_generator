# -*- coding: utf-8 -*-
import os
import re

import preprocessing
import find_keywords


def get_topic_keywords(qnas, embedding_model=None):
    """Define the topic keywords.

    Args:
        qnas (list): List of questions and answers.
        embedding_model (wordembedding.WordEmbedding): Word Embedding
            model.

    Return:
        str: Topic file content.
    """
    top_words = list()
    for question, answer in qnas:
        top_words.extend(re.sub(r'((\*~\d+)|(\(.*?\)))', ' ', question).split())
        answer_no_sw = preprocessing.remove_stopwords(answer)
        top_words.extend(find_keywords.find_entities(answer_no_sw))

    if embedding_model is not None:
        similars = list()
        for word in top_words:
            word_similars = embedding_model.get_similar(word)
            similars.extend(word_similars)

        top_words.extend(similars)

    top_words = set(top_words)
    return top_words


def generate_topic(qnas, rules, embedding_model):
    """Generate topic file content.

    Args:
        qnas (list): List of questions and answers.
        embedding_model (wordembedding.WordEmbedding): Word Embedding
            model.

    Return:
        str: Topic file content.
    """
    top_words = get_topic_keywords(qnas, embedding_model)
    top_name = 'faq.top'
    top_header = u'topic: ~{} keep repeat ({})'.format(top_name, top_words)
    return top_header + rules