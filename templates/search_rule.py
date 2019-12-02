# -*- coding: utf-8 -*-
"""Module to search rule by input."""
import re
import sys

import dataset
import preprocess


if __name__ == '__main__':
    code = 100

    db = dataset.connect('sqlite:///user_inputs.db')
    table = db['inputs']

    topic = sys.argv[2]
    user_input = sys.argv[1].replace('**', ' ')
    ppsd_input = preprocess.preprocess(user_input)

    result = table.find_one(topico=topic, entrada_processada=user_input)
    if result and result['regra']:
        code = int(re.search(r'\d+', result['regra']).group())

    # NOTE: After look for the user input in database and not found it
    #       wold be nice to find all rules and try to get the one whose
    #       most apropriate to match user input.

    exit(code)
