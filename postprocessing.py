# -*- coding: utf-8 -*-
"""Module with functions used in post processing phase"""
import os
import glob
import re


def save_topic_file(topic, botdir):
    """This method saves a topic in a file and returns its name.

    Args:
        topic (str): Topic content.
        botdir (str): Path to dir where to create topic file.
    """
    top_name = '{}.top'.format(topic.name)
    filename = os.path.join(botdir, top_name)
    with open(filename, 'w') as arq:
        arq.write(topic.__str__())


def save_control_knowledge_files(map_values, botdir):
    """Save CS control and knowledges files.

    Args:
        map_values (dict): Keys are values in template files and values
            are the actual field values in generated files.
        botdir (str): Path to dir where to create files.
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(dirname, 'templates')
    templates_filenames = glob.glob('{}*'.format(templates_dir+os.sep))

    for temp_path in templates_filenames:
        temp_name = temp_path.split(os.sep)[-1]
        result_path = os.path.join(botdir, temp_name)
        with open(temp_path, 'r') as template, open(result_path, 'w') as result:
            content = template.read()
            for temp_value, actual_value in map_values.items():
                content = content.replace(temp_value, actual_value)
            result.write(content)


def save_chatbot_files(botname, topics, cs_path='../ChatScript'):
    """This method creates the chatbot files in the passed path. If
    any of necessary directories do not exist it will be created.

    Args:
        botname (str): Name of the chatbot.
        topics (list): List of chatbot's topics content.
        cs_path (str): Path of ChatScript base directory.
    """
    rawdata = os.path.join(cs_path, 'RAWDATA')
    botname_formal = '_'.join(botname.lower().split())
    botdir = os.path.join(rawdata, botname_formal)
    if not os.path.isdir(botdir):
        os.mkdir(botdir)

    for top in topics:
        save_topic_file(top, botdir)

    map_values = {
        'BOTNAME': botname.capitalize()
    }
    save_control_knowledge_files(map_values, botdir)

    botfiles_content = os.path.join(*botdir.split(os.sep)[-2:]) + os.sep
    botfiles = os.path.join(rawdata, 'files{}.txt'.format(botname_formal))
    with open(botfiles, 'w') as arq:
        arq.write(botfiles_content)
