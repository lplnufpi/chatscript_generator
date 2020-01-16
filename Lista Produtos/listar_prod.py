import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
rows = table.find(usuario= sys.argv[1])
for row in rows:
	print(str(row['id']) + " - " + row['nome'])

