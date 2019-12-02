# -*- coding: utf-8 -*-
"""Module to preprocess input."""

STOPWORDS = [
    'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo',
    'as', 'até', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele',
    'deles', 'depois', 'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em',
    'entre', 'era', 'eram', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas',
    'este', 'estes', 'eu', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas',
    'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito', 'na', 'nas',
    'nem', 'no', 'nos', 'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa',
    'nós', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por',
    'pra', 'qual', 'quando', 'que', 'quem', 'se', 'sem', 'seu', 'seus', 'sua',
    'suas', 'só', 'também', 'te', 'tem', 'teu', 'teus', 'tu', 'tua', 'tuas',
    'um', 'uma', 'você', 'vocês', 'vos', 'à', 'às'
]


def remove_stopwords(tokens):
    """This method removes stopwords from the text.

    Args:
        text (str): Text to remove stopwords.

    Returns:
        text: Text without stopwords.
    """
    non_stopwords = [tk for tk in tokens if tk not in STOPWORDS]
    return ' '.join(non_stopwords)


def preprocess(question):
    """Do all steps of question preprocessing.

    Args:
        question (str): Original question in natural language.
        ctx_entities (list): Context entities.

    Returns:
        str: Question lower, without punctuation and with stopwords
            replaced by wildcards.
    """
    text = question.lower().split() if ' ' in question else question.lower()
    no_stopwords = remove_stopwords(text)
    no_stopwords = ' '.join(no_stopwords)

    return no_stopwords
