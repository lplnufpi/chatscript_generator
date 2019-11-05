import preprocessing

class Test(object):

    def test_wildcard_if_token_not_in(self):
        result = preprocessing.wildcard_if_token_not_in(
            'token', ['token2', 'token3']
        )
        assert result == preprocessing.WILDCARD

    def test_replace_stopwords(self):
        result = preprocessing.replace_stopwords('texto com stopword')
        expected = 'texto {} stopword'.format(preprocessing.WILDCARD)
        assert result == expected