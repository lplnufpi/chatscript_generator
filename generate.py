# -*- coding: utf-8 -*-
import topics
import add_syns
import preprocessing
import wordembedding


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


def load_ctx_entities(path):
    """Loads the context entities file and return its content as list.

    Args:
        path: Path to context entities file.

    Returns:
        list: List containg the context entities.
    """
    with open(path, 'r') as arq:
        text = arq.read().split('\n')
        return text


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


def generate_rules(qnas):
    """Generate the rules according to ChatScript sintax.

    Args:
        qnas (tuple): Tuple with question and answer.

    Yield:
        str: Rule according to ChatScript sintax.
    """
    i = 0
    for (question, answer) in qnas:
        i += 1
        rule = '\nu: U{} ({})\n\t{}'.format(i, question, answer)
        yield rule


def generate(
    questions_path='input/faqs.csv',
    ctx_entities_path='input/ctx_entities.txt'
):
    """Generate ChatScript files"""

    cbow = wordembedding.CBoW()

    ctx_entities = load_ctx_entities(ctx_entities_path)
    qnas = load_questions_answers_pairs(questions_path)

    pp_qnas = preprocess_questions(qnas, ctx_entities)
    added_syns = add_syns.add_syns(pp_qnas, cbow)
    rules = generate_rules(added_syns)
    rules_text = ''.join([rule for rule in rules])
    topic = topics.generate_topic(added_syns, rules_text, cbow)
    with open('topic.top', 'w') as arq:
        arq.write(topic)

if __name__ == '__main__':
    generate()
