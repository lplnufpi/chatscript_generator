# -*- coding: utf-8 -*-
import os

def lemmatize(text, lemmatizer_path=None):
    """This method lemmatize the text. Its used NILC's LematizadorV2a
    (http://conteudo.icmc.usp.br/pessoas/taspardo/LematizadorV2a.rar).

    Args:
        text (str): Text to be lemmatized.
        lemmatizer_path (str): Path to lemmatizer, if not passed will be
            used the default path "../../tools/LematizadorV2a".

    Returns:
        str: Lemmatized text according with LematizadorV2a output
            pattern.
    """
    if lemmatizer_path is None:
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.dirname(os.path.dirname(dirname))
        lemmatizer_path = os.path.join(dirname, 'tools', 'LematizadorV2a')

    input_file_path = os.path.join(lemmatizer_path, 'input')
    with open(input_file_path, 'w') as arq:
        arq.write(text)
    command = '{}; java -jar lematizador.jar {}'.format(
        lemmatizer_path, input_file_path
    )
    result_command = os.system(command)

    outfile = input_file_path+'.out'
    if not os.path.isfile(outfile):
        return text

    with open(outfile, 'r') as arq:
        content = arq.read()
    return content
