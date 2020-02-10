import dataset
import sys

db = dataset.connect('sqlite:///produtos.db')

nome = ' '.join(sys.argv[1:]).strip().lower()
result = db.query(
    'SELECT * FROM produto WHERE LOWER(nome) LIKE "%{}%"'.format(nome)
)

for row in result:
    text = (
        'O produto "{prod}" tem data de entrega prevista '
        'para {date} e encontra-se atualmente em {loc}.'
    ).format(prod=row['nome'], date=row['previsao_entrega'], loc=row['localizacao'])
    print(text)
