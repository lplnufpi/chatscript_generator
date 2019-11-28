# -*- coding: utf-8 -*-
"""Module to sabe usar input in database."""
import sys

import dataset
import preprocess

db = dataset.connect('sqlite:///user_inputs.db')
table = db['inputs']
entrada = sys.argv[1].replace('**', ' ')
entrada = preprocess.preprocess(entrada)
regra = sys.argv[3][1:] if len(sys.argv) == 4 else ''
topic = sys.argv[2].split('_gen')[0]

if(len(sys.argv) < 2):
    exit()
elif((len(sys.argv) == 2)):
    table.insert(dict(entrada_usuario=entrada, topico="", regra=regra))
elif((len(sys.argv) == 3)):
    table.insert(dict(entrada_usuario=entrada, topico=topic, regra=regra))
elif((len(sys.argv) == 4)):
    table.insert(dict(entrada_usuario=entrada, topico=topic, regra=regra))
