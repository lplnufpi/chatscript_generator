import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')
table = db['produto']
rows = table.find(usuario=sys.argv[1])
text = [row['nome'] for row in rows]
if text:
    print(' - {} -'.format(' - '.join(text)))
else:
    print(
        'Não foi encontrado nenhum pedido seu, '
        'por favor entre em contato por telefone'
    )