# -*- coding: utf-8 -*-
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
    answers_kwords = list()
    questions_kwords = list()
    similar_answers_kwords = list()
    similar_questions_kwords = list()

    for question, answer in qnas:
        questions_kwords.extend(
            re.sub(r'((\*~\d+)|(\[.*?\]))', ' ', question).split()
        )
        answer_no_sw = preprocessing.remove_stopwords(answer)
        answers_kwords.extend(
            find_keywords.find_entities(answer_no_sw)
        )

    if embedding_model is not None:
        for word in questions_kwords:
            word_similars = embedding_model.get_similar(word, top_n=2)
            similar_questions_kwords.extend(word_similars)

        for word in answers_kwords:
            word_similars = embedding_model.get_similar(word, top_n=2)
            similar_answers_kwords.extend(word_similars)

    result = set(
        questions_kwords + answers_kwords +
        similar_answers_kwords + similar_questions_kwords
    )
    return result


def generate_topic(qnas, rules_text, embedding_model):
    """Generate topic file content.

    Args:
        qnas (list): List of questions and answers.
        gen_qnas (list): List of generalizeds questions.
        embedding_model (wordembedding.WordEmbedding): Word Embedding
            model.

    Return:
        str: Topic file content.
    """
    keywords = get_topic_keywords(qnas, embedding_model)
    top_keywords = ' '.join(keywords)
    top_name = 'faq'
    top_header = u'topic: ~{} keep repeat ({})\n\n'.format(
        top_name, top_keywords
    )
    return top_header + rules_text
