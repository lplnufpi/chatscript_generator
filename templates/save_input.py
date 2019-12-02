# -*- coding: utf-8 -*-
"""Module to sabe usar input in database."""
import sys

import dataset
import preprocess

db = dataset.connect('sqlite:///user_inputs.db')
table = db['inputs']
entrada_original = sys.argv[1].replace('**', ' ')
entrada_processada = preprocess.preprocess(entrada_original)
regra = sys.argv[3][1:] if len(sys.argv) == 4 else ''
topic = sys.argv[2].split('_gen')[0]

if(len(sys.argv) < 2):
    exit()
elif((len(sys.argv) == 2)):
    table.insert({
        'entrada_original': entrada_original,
        'entrada_processada': entrada_processada,
        'topico': "",
        'regra': regra
    })
elif((len(sys.argv) == 3)):
    table.insert({
        'entrada_original': entrada_original,
        'entrada_processada': entrada_processada,
        'topico': topic,
        'regra': regra
    })
elif((len(sys.argv) == 4)):
    table.insert({
        'entrada_original': entrada_original,
        'entrada_processada': entrada_processada,
        'topico': topic,
        'regra': regra
    })
