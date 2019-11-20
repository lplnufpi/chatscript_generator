import dataset
import sys

db = dataset.connect('sqlite:///user_inputs.db')
#Muda o nome do DB
table = db['inputs']
entrada = sys.argv[1].replace('**', ' ')

if(len(sys.argv) < 2):
    exit()
elif((len(sys.argv) == 2)):
    table.insert(dict(entrada_usuario=entrada, topico="", regra=""))
elif((len(sys.argv) == 3)):
    table.insert(dict(entrada_usuario=entrada, topico=sys.argv[2], regra=""))
elif((len(sys.argv) == 4)):
    table.insert(dict(entrada_usuario=entrada, topico=sys.argv[2], regra=sys.argv[3]))
