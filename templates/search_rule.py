# -*- coding: utf-8 -*-
"""Module to search rule by input."""
import re
import sys

import dataset
import preprocess


code = 100
db = dataset.connect('sqlite:///user_inputs.db')
table = db['inputs']

input_original = sys.argv[1].replace('**', ' ')
input_pcsd = preprocess.preprocess(input_original)
topic = sys.argv[2].split('_gen')[0]

result = table.find_one(topic=topic, input_processed=input_pcsd)
if result and result['rule']:
    code = int(re.search(r'\d+', result['rule']).group())

    # Update requisitions count
    requisitions = result['requisitions'] + 1
    table.update(dict(requisitions=requisitions, id=result['id']), ['id'])

# NOTE: After look for the user input in database and not found it
#       wold be nice to find all rules and try to get the one whose
#       most apropriate to match user input.

exit(code)
