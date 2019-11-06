# -*- coding: utf-8 -*-
import re

import nltk
import string

from utils import stopwords


WILDCARD_DEFAULT_VALUE = 1
WILDCARD_MASK = u'*~{}'
WILDCARD = WILDCARD_MASK.format(WILDCARD_DEFAULT_VALUE)


def wildcard_if_token_not_in(token, words):
    """Returns the wildcard if token is NOT IN the list of words.

    Args:
        token (str): Word to be analised.
        words (list): List of words that the token must be in to not
            return wildcard.

    Returns:
        str: Token or wildcard if token not in words.
    """
    return token if token in words else WILDCARD


def remove_punctation(tokens):
    """This method removes punctuation from the text.

    Args:
        tokens (list): List of tokens to remove punctuation.

    Returns:
        list: List of tokens without punctuation.
    """
    non_stopwords = []
    for token in tokens:
        if token not in string.punctuation:
            non_stopwords.append(token)
    return non_stopwords


def remove_stopwords(text):
    """This method removes stopwords from the text.

    Args:
        text (str): Text to remove stopwords.

    Returns:
        text: Text without stopwords.
    """
    tokens = nltk.word_tokenize(text)
    non_stopwords = [tk for tk in tokens if tk not in stopwords.stopwords]
    return ' '.join(non_stopwords)


def replace_stopwords(tokens):
    """This method replaces stopwords from the text by wildcard.

    Args:
        tokens (list): List of tokens to remove punctuation.

    Returns:
        list: List of tokens without punctuation.
    """
    non_stopwords = []
    for token in tokens:
        new_token = token if token not in stopwords.stopwords else WILDCARD
        non_stopwords.append(new_token)
    return non_stopwords


def add_wildcards(text):
    """Sum the consecutive wildcards and replace them by the result.

    Args:
        text (str): Text.

    Returns:
        str: Text with added wildcards.
    """
    followed_wd = re.search(r'(\*~\d+ ?){2,}', text)

    while followed_wd:
        followed_wd_text = followed_wd.group().strip()
        wd_values = re.findall(r'\*~(\d+)', followed_wd_text)
        wd_added = sum([int(wd_value) for wd_value in wd_values])
        text = text.replace(followed_wd_text, WILDCARD_MASK.format(wd_added))
        followed_wd = re.search(r'(\*~\d+ ?){2,}', text)

    return text


def replace_context_entities(ctx_entities, text):
    """Search form context entities in the text and join them with
    underscore.

    Args:
        text (str): Text.

    Returns:
        list: List of tokens with context entities undescored.
    """
    for entity in ctx_entities:
        text = text.replace(entity, '_'.join(entity.split()))
    return text


def preprocess(question, ctx_entities):
    """Do all steps of question preprocessing.

    Args:
        question (str): Original question in natural language.
        ctx_entities (list): Context entities.

    Returns:
        str: Question lower, without punctuation and with stopwords
            replaced by wildcards.
    """
    rplcd_ctx_entities = replace_context_entities(
        ctx_entities, question.lower()
    )
    tokens = nltk.word_tokenize(rplcd_ctx_entities)
    no_punctuation = remove_punctation(tokens)
    no_stopwords = replace_stopwords(no_punctuation)
    no_stopwords = ' '.join(no_stopwords)
    added_wildcards = add_wildcards(no_stopwords)

    return added_wildcards
