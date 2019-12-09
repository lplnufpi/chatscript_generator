# -*- coding: utf-8 -*-
import unicodedata
import wordembedding

VOGAIS = [
    b'a', b'e', b'i', b'o', b'u'
]
VOGAIS_ORAIS = ['a', 'e', 'é', 'ê', 'i', 'i', 'o', 'ó', 'ô','u']


def ditongo_oral(word):
    return word[-1] in VOGAIS_ORAIS and word[-2] in VOGAIS_ORAIS

def is_vogal(letter):
    letter = unicodedata.normalize(u'NFKD', letter).encode(u'latin1', u'ignore')
    return letter in VOGAIS


def _get_word_plurals(word):
    plurals = list()
    word = word.lower()

    # Terminadas em vogais antecedidas por consoantes ou ditongos orais
    if (
        (is_vogal(word[-1]) and (not is_vogal(word[-2]) or ditongo_oral(word)))
        or word[-1] == 'n'
    ):
        plurals.append(word + 's')
    if word[-1] == 'm':
        plurals.append(word[:-1] + 'ns')
    if word[-1] in ['r', 'z']:
        plurals.append(word + 'es')
    if word[-1] == 'l':
        if word[-2] in ['a', 'e', 'o', 'u']:
            if word == 'mal':
                plurals.append('males')
            elif word == 'cônsul':
                plurals.append('cônsules')
            else:
                plurals.append(word[:-1] + 'is')
        if word[-2] == 'i':
            plurals.append(word[:-1] + 's')
            plurals.append(word[:-2] + 'eis')
    if word.endswith('ão'):
        plurals.append(word[:-2] + 'ões')
        plurals.append(word[:-2] + 'ães')
        plurals.append(word[:-2] + 'âos')
    if word.endswith('x'):
        plurals.append(word)

    return plurals

def get_plurals(word, cbow=None):
    if cbow is None:
        print('WORDEMBEDDING MODEL BEEN INSTANCED')
        cbow = wordembedding.CBoW()

    word_plurals = _get_word_plurals(word)
    plurals = list()

    for plural in word_plurals:
        try:
            sim = cbow.model.similarity(word, plural)
        except KeyError:
            sim = 0
        plurals.append((plural, sim))
    if plurals:
        plurals.sort(key=lambda p: p[1], reverse=True)
        return plurals[0][0]
    return None
