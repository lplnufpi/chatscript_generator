# -*- coding: utf-8 -*-
import os
import glob

import models
import preprocessing
import wordembedding
import postprocessing
import generalize_rules
from utils import plural_singular


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
    for line in input_lines[1:]:
        line_parts = line.split(',')

        title = line_parts[0]

        answer = ','.join(line_parts[2:])
        question = line_parts[1].lower() if lower else line_parts[1]
        questions.append((title, question, answer))

    return input_lines[0], questions


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


def generate_topic_menu(topics, cbow):
    names = list()
    rejoinders = list()
    for topic in topics:
        if topic.beauty_name:
            names.append(topic.beauty_name)
            options = list()
            options_rule = list()
            for rule in topic.rules:
                if rule.title:
                    options.append(rule.title)
                    output = '^reuse(~{}.{})'.format(topic.name, rule.label)
                    options_rule.append(
                        '\n\t\t\t\tb: ({pattern}) {output}'.format(
                            pattern=rule.title, output=output
                        )
                    )

            # Join options
            options =  '\n\t\t\t- '.join(options)
            options_text = (
                '\n\t\t\t^pick(~all_right), aqui estão opções relacionadas a '
                '"{entity}":\n\t\t\t- {options}'
            ).format(entity=topic.beauty_name, options=options)
            options_rule = ''.join(options_rule)

            name = topic.beauty_name.lower()
            plural = ''
            for subname in name.split(' '):
                plural_sub = plural_singular.get_plurals(subname, cbow=cbow)
                if plural_sub:
                    plural = plural + ' ' + plural_sub
            pattern = '[{} {}]'.format(name, plural) if plural else name

            rej = 'a: ({pattern}){options_text}{options_rule}'.format(
                pattern=pattern,
                options_text=options_text,
                options_rule=options_rule,
            )
            rejoinders.append(rej)

    topics_names = '- {}'.format('\n\t- '.join(names))

    class TopicMenu(object):
        name = None
        head = None
        rejoinders = None

        def __init__(self, head, rejoinders):
            self.name = 'menu'
            self.head = head
            self.rejoinders = rejoinders

        def __str__(self):
            topic_text = (
                'topic: ~menu keep repeat ()\n'
                'u: () Posso lhe dar informações sobre:'
                '\n\t{head}\n\t- Falar com um atendente -'
                '\n\t\t{rejoinders}\n\t\ta: (<<falar atendente>>)'
                '\n\t\t\t^pick(~all_right), ^pick(~tranfeer).'
            ).format(
                head=self.head, rejoinders=self.rejoinders
            )
            return topic_text

    menu = TopicMenu(topics_names, '\n\t\t'.join(rejoinders))
    return menu

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
        beaty_topic_name, questions = load_questions(questions_path)
        rules = generate_rules(questions, ctx_entities, cbow)

        sorted_rules = generalize_rules.sort_by_entities(rules, cbow)

        top_name = questions_path.split(os.sep)[-1].split('.')[0]
        topic = models.Topic(top_name, rules, beauty_name=beaty_topic_name)

        gen_rules = generalize_rules.generalize(topic, cbow)
        gen_topic = models.Topic(top_name+'_gen', gen_rules)

        topic.rules.extend(sorted_rules)

        generetad_topics.append(topic)
        generetad_topics.append(gen_topic)

    menu = generate_topic_menu(generetad_topics, cbow)
    generetad_topics.append(menu)
    postprocessing.save_chatbot_files('Botin', generetad_topics)


if __name__ == '__main__':
    generate()
