import csv
import dataset

f = open('produtos.csv', 'r')
db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
table.delete()
with f:
    reader = csv.DictReader(f)
    for row in reader:
        table.insert(dict(row))