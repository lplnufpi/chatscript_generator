# -*- coding: utf-8 -*-
import os
import glob

import models
import preprocessing
import wordembedding
import postprocessing


def load_file(path):
    """Loads file and return its content as list.

    Args:
        path: Path to file.

    Returns:
        list: Content splited by linebreak.
    """
    with open(path, 'r') as arq:
        text = arq.read().split('\n')
        return text


def load_questions(path, lower=True):
    """Loads the questions file and return a tuple containing
    a list of questions titles and list of tuples containing questions
    and answers.

    Args:
        path: Path to questions file.

    Returns:
        List: List of tuples containg titles, questions and answers.
    """
    questions = list()
    input_lines = load_file(path)
    for line in input_lines:
        line_parts = line.split(',')

        title = line_parts[0]

        answer = ','.join(line_parts[2:])
        question = line_parts[1].lower() if lower else line_parts[1]
        questions.append((title, question, answer))

    return questions


def preprocess_questions(qnas, ctx_entities):
    """Preprocess all the questions.

    Args:
        qnas (tuple): Tuple with question and answer.
        ctx_entities (list): List of context entities.

    Yield:
        tuple: Tuple containing preprocessed question and answer.
    """
    for (question, answer) in qnas:
        pp_question = preprocessing.preprocess(question, ctx_entities)
        yield pp_question, answer


def generate_rules(qnas, ctx_entities, embedding_model):
    """Generate the rules according to ChatScript sintax.

    Args:
        qnas (list): List of tuple with title, question and answer.
        ctx_entities (list): Context entities.

    Yield:
        str: Rule according to ChatScript sintax.
    """
    rules = list()
    for rule_id, (title, question, answer) in enumerate(qnas):
        rule = models.Rule(
            rule_id,
            title,
            question,
            answer,
            ctx_entities,
            embedding_model
        )
        rules.append(rule)
    return rules


def generate(
    ctx_entities_path='input/ctx_entities.txt'
):
    """Generate ChatScript files"""
    input_files = list()
    dirname = os.path.dirname(os.path.abspath(__file__))
    dirname = os.path.join(dirname, 'input')
    input_files = glob.glob('{}*.csv'.format(dirname+os.sep))

    generetad_topics = list()
    cbow = wordembedding.CBoW()
    ctx_entities = load_file(ctx_entities_path)

    for questions_path in input_files:
        questions = load_questions(questions_path)
        rules = generate_rules(questions, ctx_entities, cbow)

        top_name = questions_path.split(os.sep)[-1].split('.')[0]
        topic = models.Topic(top_name, rules)
        topic.generalize_rules(cbow)

        generetad_topics.append(topic)

    postprocessing.save_chatbot_files('Botin', generetad_topics)


if __name__ == '__main__':
    generate()
