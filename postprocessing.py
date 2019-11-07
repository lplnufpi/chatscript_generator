# -*- coding: utf-8 -*-
"""Module with functions used in post processing phase"""
import os
import re


def save_topic_file(topic, botdir):
    """This method saves a topic in a file and returns its name.

    Args:
        topic (str): Topic content.
        botdir (str): Path to dir where to create topic file.

    Returns:
        str: Topic's name.
    """
    top = re.search(r'topic: ~(.*?) ', topic).group(1)
    top_name = '{}.top'.format(top)
    filename = os.path.join(botdir, top_name)
    with open(filename, 'w') as arq:
        arq.write(topic)

    return top_name


def save_control_knowledge_files(botname, botdir):
    """Save CS control and knowledges files.

    Args:
        botdir (str): Path to dir where to create files.

    Returns:
        list: list of creted file's names.
    """
    return []


def save_chatbot_files(botname, topics, cs_path='../ChatScript'):
    """This method creates the chatbot files in the passed path. If
    any of necessary directories do not exist it will be created.

    Args:
        botname (str): Name of the chatbot.
        topics (list): List of chatbot's topics content.
        cs_path (str): Path of ChatScript base directory.
    """
    filenames = list()
    rawdata = os.path.join(cs_path, 'RAWDATA')
    botdir = os.path.join(rawdata, botname.upper())
    if not os.path.isdir(botdir):
        os.mkdir(botdir)

    for top in topics:
        top_name = save_topic_file(top, botdir)
        filenames.append(top_name)

    filenames.extend(save_control_knowledge_files(botname, botdir))

    botfiles_content = '\n'.join(filenames)
    botfiles = os.path.join(rawdata, 'files{}.txt'.format(botname))
    with open(botfiles, 'w') as arq:
        arq.write(botfiles_content)
