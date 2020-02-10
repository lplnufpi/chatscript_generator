import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
row = table.find_one(id= sys.argv[1])
text = (
    'O produto "{prod}" tem data de entrega prevista '
    'para {date} e encontra-se atualmente em {loc}.'
).format(prod=row['nome'], date=row['previsao_entrega'], loc=row['localizacao'])
print(text)
