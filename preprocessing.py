import nltk

from utils import stopwords


WILDCARD_DEFAULT_VALUE = 1
WILDCARD = u'*~{}'.format(WILDCARD_DEFAULT_VALUE)

def wildcard_if_token_not_in(token, words):
    """Returns the wildcard if token is NOT IN the list of words.

    Args:
        token (str): Word to be analised.
        words (list): List of words that the token must be in to not
            return wildcard.

    Returns:
        str: Token or wildcard if token not in words.
    """
    return token if token in words else WILDCARD

def replace_stopwords(text):
    """This method replaces stopwords from the text by wildcard.

    Args:
        text (str): Text to replace stopwords.

    Returns:
        str: Text with stopwords replaced by wildcard.
    """
    tokens = nltk.word_tokenize(text)
    non_stopwords = []
    for token in tokens:
        new_token = token if token not in stopwords.stopwords else WILDCARD
        non_stopwords.append(new_token)
    return ' '.join(non_stopwords)