import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
row = table.find_one(id= sys.argv[1])
print("O produto " + row['nome'] +  " tem data de entrega prevista para " + row['previsao_entrega'] + " e se encontra atualmente em " + row['localizacao'] + ".")


