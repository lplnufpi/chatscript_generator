# -*- coding: utf-8 -*-
import os
import shutil
import nltk
import regex
import pickle
import glob


def tag_text(text=None, tokens=None):
    tokens = nltk.word_tokenize(text) if tokens is None else tokens
    tags = TAGGER.tag(tokens)
    return tags

def write_concepts(concepts_file):
    stopwords = u' '.join(STOPWORDS)
    sw_concept = u'concept: ~stopword [{}]'.format(stopwords)
    concepts_file.write(sw_concept.encode(u'utf-8'))
    concepts_file.close()

def load_domain_nouns(path='domain_nouns.txt'):
    """This method returns an dict where the keys are the new domain
    nouns and the values are old domain nouns.

    Args:
        path: Path to domain nouns file.

    Returns:
        dict: An dict like {'domain_noun': 'Domain Noun'}.
    """
    with open(path, 'r') as arq:
        lines = arq.read().lower().split('\n')
        lines = [(regex.sub(' ', '_', line), line) for line in lines]
    return dict(lines)

def encode_domain_nouns(text, domain_nouns):
    """This method replaces domain names with new formats.

    Args:
        text (unicode): Text where the domain nouns will be replaced.
        domain_nouns (dict): Dictionary containing the new and former
            domain nouns.

    Returns:
        unicode: Text with the domain nouns replaced.

    Examples:
        >>> replace_domain_nouns(
            u'Domain Noun bla bla bla', {u'domain_noun': u'Domain Noun'}
        )
        u'domain_noun bla bla bla'
    """

    for new_noun, former_noun in domain_nouns.items():
        text = regex.sub(former_noun, new_noun, text)

    return text

def decode_domain_nouns(text, domain_nouns):
    """This method replaces new formats with the former domain names.

    Args:
        text (unicode): Text where the domain nouns will be replaced.
        domain_nouns (dict): Dictionary containing the new and former
            domain nouns.

    Returns:
        unicode: Text with the domain nouns replaced.

    Examples:
        >>> replace_domain_nouns(
            u'domain_noun bla bla bla', {u'domain_noun': u'Domain Noun'}
        )
        u'Domain Noun bla bla bla'
    """

    for new_noun, former_noun in domain_nouns.items():
        text = regex.sub(new_noun, former_noun, text)

    return text

def load_synonyms(path='synonyms.txt'):
    with open(path, 'r') as arq:
        text = arq.read()
        synset = list()
        regex_synset = regex.findall('\{.*\}', text)
        for syn in regex_synset:
            aux_syn = regex.sub('(\{|\})', '', syn)
            synset.append(regex.sub(', ', '|', aux_syn))
        return synset

def load_questions(path='faq.csv', domain_nouns={}):
    with open(path, 'r') as arq:
        text = arq.read().split('\n')
        lines = list()
        for t in text:
            w = t.split(',')
            lines.append((w[0].lower(), ','.join(w[1:])))
        return lines

def create_files(topics):
    if not os.path.exists('FAQ'):
        os.makedirs('FAQ')

    files = open('filesfaq.txt', 'w')
    lines = [
        'RAWDATA/FAQ/simplecontrol.top\n',
        'RAWDATA/FAQ/introductions.top\n',
        'RAWDATA/FAQ/concepts.top\n'
    ]
    for top in topics:
        lines.append('{}.top'.format(top))
    files.writelines(lines)
    files.close()

    shutil.copyfile('simplecontrol.top', 'FAQ/simplecontrol.top')
    shutil.copyfile('introductions.top', 'FAQ/introductions.top')
    return open('FAQ/concepts.top', 'w')

def remove_stopwords(text):
    tokens = nltk.word_tokenize(text)
    stopwords = STOPWORDS
    non_stopwords = [tk for tk in tokens if tk not in stopwords]

    return ' '.join(non_stopwords)

def remove_punctuation(text):
    no_punctuation = regex.sub('[.,!?]', '', text)
    return no_punctuation

def remove_no_desired_freq_words(text):
    return regex.sub(ur'( centaurocombr| é| -)', '', text)

def get_topic_words(lines):
    questions = [q for (q, a) in lines]
    text = unicode(' '.join(questions).lower(), 'utf-8')
    text = remove_stopwords(text)
    text = remove_punctuation(text)
    text = remove_no_desired_freq_words(text)
    tokens = nltk.word_tokenize(text)
    fdist = nltk.FreqDist(nltk.Text(tokens))
    topic_words = [word for (word, dist) in fdist.most_common(TOPIC_WORDS)]
    return ' '.join(topic_words)

def replace_stopword_with_wildcard(token):
    text = token if token not in STOPWORDS else WILDCARD.encode()
    return text

def replace_consecutive_wildcards(text):
    """This method replaces consecutive wildcards(not allowed by
    chatscript) with one single wildcard.

    Examples:
        >>> remove_consecutive_wildcards("*~1 *~1 asdf *~1 *~1 *~1 fdsa")
        "*~2 asdf *~3 fdsa"
    """
    pattern = '(\*~{value} ?){{2,}}'.format(value=WILDCARD_DEFAULT_VALUE)
    wildcard_regex = regex.search(pattern, text)

    # A cada iteração é encontrada e substituída a ocorrência de
    # wildcards consecutivos mais à esquerda do texto
    while wildcard_regex is not None:
        wildcard_match = wildcard_regex.group()
        repetition = len(wildcard_match.split())
        # O novo wildcard terá o valor do antigo multiplicado pelo
        # número de repetições dele.
        new_wildcard = '*~{} '.format(WILDCARD_DEFAULT_VALUE*repetition)
        wildcard_match = regex.sub('\*', '\\*', wildcard_match)
        # Substituir somente a primeira ocorrência do padrão para que as
        # demais sejam calculadas e substituidas nas próximas iterações
        new_text = regex.sub(wildcard_match, new_wildcard, text, 1)
        if new_text != text:
            text = new_text
            wildcard_regex = regex.search(pattern, text)
        else:
            break

    return text

def get_syns(word):
    from collections import Counter
    from itertools import repeat, chain
    subsynset = [synset for synset in SYNONYMS if word in synset]
    subsynset = '|'.join(subsynset)
    subsynset = list(chain.from_iterable(repeat(i, c) for i,c in Counter(subsynset.split('|')).most_common()))
    subsynset = [word] + list(set(subsynset[:SYNONYMS_LIMIT]) - {word})
    subsynset = [s for s in subsynset if s]
    return '|'.join(subsynset) if len(subsynset) > 1 else []

def replace_syns(text, synset):
    for word, syns in synset:
        if syns:
            text = regex.sub(word, '({})'.format(syns), text)

    return text

def prepare_question(text, domain_nouns={}):
    text = encode_domain_nouns(text, domain_nouns)
    tokens = nltk.word_tokenize(text)
    question = map(replace_stopword_with_wildcard, tokens)
    question = ' '.join(question)
    question = replace_consecutive_wildcards(question)
    tagged_text = tag_text(question)
    syns = [(word, get_syns(word)) for word, tag in tagged_text if tag=='VERB']
    question = replace_syns(question, syns)

    return question

def get_topic_name(filename):
    return filename.split('.')[1][1:]

def generate():
    domain_nouns = load_domain_nouns()
    paths = glob.glob('./*.csv')
    topics = [get_topic_name(t) for t in paths]

    concept_file = create_files(topics)
    write_concepts(concept_file)

    for path in paths:
        topic_name = get_topic_name(path)
        questions = load_questions(path=path, domain_nouns=domain_nouns)
        topic_words = get_topic_words(questions)

        text = u'topic: ~{} keep repeat ({})'.format(topic_name, topic_words)
        for i in range(len(questions)):
            answer = unicode(questions[i][1], 'utf-8')
            question = prepare_question(questions[i][0].lower(), domain_nouns)
            text += u'\nu: U{} ({})\n{}'.format(i, unicode(question, 'utf-8'), answer)

        with open('FAQ/{}.top'.format(topic_name), 'w') as faq_file:
            faq_file.write(text.encode(u'utf-8'))

STOPWORDS = nltk.corpus.stopwords.words('portuguese')
WILDCARD_DEFAULT_VALUE = 1
WILDCARD = u'*~{}'.format(WILDCARD_DEFAULT_VALUE)
TOPIC_WORDS = 15
TAGGER = pickle.load(open("tagger.pkl"))
PT_TOKENIZER = nltk.data.load("tokenizers/punkt/portuguese.pickle")
SYNONYMS = load_synonyms()
SYNONYMS_LIMIT = 10

if __name__ == '__main__':
    generate()