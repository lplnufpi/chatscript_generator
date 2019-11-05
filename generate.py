# -*- coding: utf-8 -*-
import re
import nltk

import preprocessing
import find_keywords
from word2vec import word2vec


def load_questions_answers_pairs(path):
    """Loads the questions file and return a list of tuples containing
    questions and answers.

    Args:
        path: Path to questions file.

    Returns:
        list: List of tuples containg questions and answers.
    """
    with open(path, 'r') as arq:
        text = arq.read().split('\n')
        lines = list()
        for t in text:
            w = t.split(',')
            lines.append((w[0].lower(), ','.join(w[1:])))
        return lines


def get_syns(words, embedding):
    """Get the synonyms to the words by embedding.

    Args:
        words (list): List of words to get their syns.
        embedding (word2vec.Word2Vec): Trained word2vec model.

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
        intentions_text = '({})'.format('|'.join(intentions))
        question = question.replace(intention, intentions_text)

    return question


def do_preprocessing(question):
    no_stopwords = preprocessing.replace_stopwords(question)
    # correção gramatical
    # remoção de pontuação
    return no_stopwords


def generate_rules(qna, embedding):
    """Generate the rules"""
    i = 0
    rules = list()
    for (question, answer) in qna:
        pprd_question = do_preprocessing(question)
        no_stopwords = re.sub(r'\*~\d+', '', pprd_question)
        no_stopwords = ' '.join(nltk.word_tokenize(no_stopwords))

        entities = find_keywords.find_entities(no_stopwords)
        intentions = find_keywords.find_intention(no_stopwords, entities)
        intentions_syns = get_syns(intentions, embedding)
        question_rule = add_intentions_syns(pprd_question, intentions_syns)

        rule = '\nu: U{} ({})\n{}'.format(i, question_rule, answer)
        rules.append(rule)
        i += 1

    return rules


def generate(path='faqs.csv'):
    cbow = word2vec.CBoW()
    qnas = load_questions_answers_pairs(path)
    rules = generate_rules(qnas, cbow)
    import pdb;pdb.set_trace()

if __name__ == '__main__':
    generate()