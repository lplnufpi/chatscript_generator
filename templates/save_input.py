# -*- coding: utf-8 -*-
"""Module to sabe usar input in database."""
import sys

import dataset
import preprocess

db = dataset.connect('sqlite:///user_inputs.db')
table = db['inputs']

input_original = sys.argv[1].replace('**', ' ')
input_pcsd = preprocess.preprocess(input_original)
topic = sys.argv[2].split('_gen')[0] if len(sys.argv) >=3 else None
rule = sys.argv[3][1:] if len(sys.argv) == 4 else None

table.insert({
    'input_original': input_original,
    'input_processed': input_pcsd,
    'topic': topic,
    'rule': rule,
    'requisitions': 0
})
