# -*- coding: utf-8 -*-
import re

import find_keywords


def get_syns(words, embedding):
    """Get the synonyms to the words by embedding.

    Args:
        words (list): List of words to get their syns.
        embedding (wordembbeding.WordEmbbeding): Trained Word Embbeding
            model.

    Returns:
        dict: Dictionar containing the words and their syns.
    """
    syns = dict()
    for word in words:
        syns[word] = embedding.get_similar(word)
    return syns


def add_intentions_syns(question, intentions_syns):
    """Replace every intention in the question by it and its syns in
    ChatScript sintax.

    Args:
        questions (str): Text to be changed.
        intentions_syns (dict): Intentions and their syns.

    Returns:
        str: The question with syns.
    """
    for intention in intentions_syns.keys():
        intentions = [intention] + intentions_syns[intention]
        intentions_text = '[{}]'.format(' '.join(intentions))
        question = question.replace(intention, intentions_text)

    return question


def add_syns(qnas, embedding_model):
    """Preprocess all the questions.

    Args:
        qnas (tuple): Tuple with question and answer.
        embedding_model (wordembedding.WordEmbedding): Word Embedding
            model.

    Returns:
        list[tuple]: List of tuples containing questions with replaced
            syns and its answers.
    """
    added_syns = list()
    for (question, answer) in qnas:
        no_wildcards = re.sub(r'\*~\d+', '', question)
        entities = find_keywords.find_entities(no_wildcards)
        intentions = find_keywords.find_intention(no_wildcards, entities)

        intentions_syns = get_syns(intentions, embedding_model)
        question_with_syns = add_intentions_syns(question, intentions_syns)

        added_syns.append((question_with_syns, answer))

    return added_syns
