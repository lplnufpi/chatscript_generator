# -*- coding: utf-8 -*-
import os
import glob

import topics
import add_syns
import preprocessing
import wordembedding
import postprocessing
import generalize_rules


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
        tutple: List of questions titles and list of tuples containg
            questions and answers.
    """
    questions = list()
    titles = list()
    input_lines = load_file(path)
    for line in input_lines:
        line_parts = line.split(',')

        title = line_parts[0]
        titles.append(title)

        answer = ','.join(line_parts[2:])
        question = line_parts[1].lower() if lower else line_parts[1]
        questions.append((question, answer))

    return titles, questions


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


def generate_rules(qnas, label='U'):
    """Generate the rules according to ChatScript sintax.

    Args:
        qnas (tuple): Tuple with question and answer.

    Yield:
        str: Rule according to ChatScript sintax.
    """
    i = 0
    for (question, answer) in qnas:
        i += 1
        rule = '\nu: {}{} ({})\n\t{}'.format(label, i, question, answer)
        yield rule


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
        titles, questions = load_questions(questions_path)

        pp_qnas = preprocess_questions(questions, ctx_entities)
        original_rules = add_syns.add_syns(pp_qnas, cbow)
        original_rules_text = ''.join(
            [rule for rule in generate_rules(original_rules)]
        )

        question_rules = [q for (q, a) in original_rules]
        _, question_original = load_questions(
            questions_path, lower=False
        )
        question_original = [q for (q, a) in question_original]
        gen_rules = generalize_rules.generalize(
            question_rules, question_original, cbow, titles
        )

        rules_text = '{}\n\n\n{}'.format(original_rules_text, gen_rules)
        topic = topics.generate_topic(original_rules, rules_text, cbow)
        generetad_topics.append(topic)

    postprocessing.save_chatbot_files('Botin', generetad_topics)


if __name__ == '__main__':
    generate()
