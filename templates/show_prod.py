import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
rows = table.find(usuario=sys.argv[1])
text = [row['nome'] for row in rows]
print(' - {} -'.format(' - '.join(text)))