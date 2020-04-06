import re
import nlpnet
import logging


nlpnet.set_data_dir('../pos-pt')
tagger = nlpnet.POSTagger()


def tag_text(text):
    """Add tags to passed text.

    Args:
        text (str): Text to be tagged.

    Return:
        str: Tagged text.

    Example:
        >>> tag_text('Bom dia')
        'Bom/ADJ dia/N'
    """
    if text.replace(' ', ''):
        try:
            tags = tagger.tag(text)[0]
            tagged_text = ' '.join(['{}/{}'.format(x,y) for (x, y) in tags])
            return tagged_text
        except:
            logging.exception(u'Error tagging text: "%s"', text)

    return ''


def has_tags(word, tags):
    """Verify if word has tag.
    """
    tag = word.split('/')[-1]
    return tag in tags


def flatten_list(items):
    result = list()
    for item in items:
        for subitem in item:
            result.append(subitem)
    return result


def is_substring(substring, strings):
    for string in strings:
        if substring in string and substring!=string:
            return True
    return False


def find_entities(text):
    entities = list()
    tagged_text = tag_text(text)
    tagged_entities = re.findall(
        r'(\w+/ADJ (\w+/PREP)?)?'
        r'('
            r'((\w+/N ?)+ (\w+/ADJ ?)*)|'
            r'((\w+/NPROP ?)+)|'
            r'(\w+/PCP)'
        r')',
        tagged_text
    )
    if tagged_entities:
        flatten = flatten_list(tagged_entities)
        striped = set(ent.strip() for ent in flatten if ent!='')
        no_tags = [re.sub(r'/\w+', '', ent) for ent in striped]
        # remove substrings
        entities = [ent for ent in no_tags if not is_substring(ent, no_tags)]

    return entities


def get_closer(tagged_words):
    distance = 0
    for tagged_word in tagged_words:
        distance += 1
        if tagged_word.strip().endswith('/V'):
            return distance, tagged_word[:-2]

    return 1000, None


def find_intention(text, entities):
    intentions = list()

    for entity in entities:
        splited = text.split(entity)
        pre = tag_text(splited[0])
        pos = tag_text(splited[-1]) if len(splited) > 1 and splited[-1] else ''

        tagged_pre = re.findall(r'(\w+/V)', pre)
        tagged_pre.reverse()
        tagged_pos = re.findall(r'(\w+/V)', pos)

        dist_pre, closer_pre = get_closer(tagged_pre)
        dist_pos, closer_pos = get_closer(tagged_pos)

        if closer_pre and closer_pos:
            intention = closer_pre if dist_pre < dist_pos else closer_pos
        elif closer_pre and not closer_pos:
            intention = closer_pre
        elif not closer_pre and closer_pos:
            intention = closer_pos
        else:
            intention = None

        if intention is not None:
            intentions.append(intention)

    return list(set(intentions))



if __name__ == '__main__':
    # text = 'Como verificar minha conta bancária'
    # text = 'Como faço uma venda por boleto bancário?'
    text = 'Posso pagar minhas compras com pontos e reais no mesmo pedido?'
    ent = find_entities(text)
    intention = find_intention(text, ent)
    print(ent)
    print(intention)