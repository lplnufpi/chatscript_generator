# -*- coding: utf-8 -*-
import topics
import add_syns
import preprocessing
import wordembedding
import postprocessing
import generalize_rules


def load_questions_answers_pairs(path, lower=True):
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
            if lower:
                lines.append((w[0].lower(), ','.join(w[1:])))
            else:
                lines.append((w[0], ','.join(w[1:])))
        return lines


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
    questions_path='input/faqs.csv',
    ctx_entities_path='input/ctx_entities.txt',
    questions_titles_path='input/faqs_titles.txt'
):
    """Generate ChatScript files"""

    cbow = wordembedding.CBoW()

    ctx_entities = load_file(ctx_entities_path)
    qnas = load_questions_answers_pairs(questions_path)
    questions_titles = load_file(questions_titles_path)

    pp_qnas = preprocess_questions(qnas, ctx_entities)
    original_rules = add_syns.add_syns(pp_qnas, cbow)
    original_rules_text = ''.join(
        [rule for rule in generate_rules(original_rules)]
    )

    question_rules = [q for (q, a) in original_rules]
    question_original = load_questions_answers_pairs(
        questions_path, lower=False
    )
    question_original = [q for (q, a) in question_original]
    gen_rules = generalize_rules.generalize(
        question_rules, question_original, cbow, questions_titles
    )

    rules_text = '{}\n\n\n{}'.format(original_rules_text, gen_rules)
    topic = topics.generate_topic(original_rules, rules_text, cbow)
    postprocessing.save_chatbot_files('Botin', [topic])


if __name__ == '__main__':
    generate()
