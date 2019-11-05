from gensim.models import KeyedVectors


class Word2Vec(object):
    """Class to use the functions of Word2Vec models."""
    model = None

    def get_similar(self, word, top_n=3):
        """This method returns the TOP_N most similar words.

        Args:
            word (str): Word about which you want to get similar ones.
            top_n (int): Quantity of the most similar words to be
                returned.

        Returns:
            list[str]: List of TOP_N most similar words.
        """
        # try:
        most_similar = self.model.most_similar(word)
        top_similar = [x for (x, _) in most_similar[:top_n]]
        return top_similar
        # except KeyError:
            # return []


class CBoW(Word2Vec):

    def __init__(self):
        self.model = KeyedVectors.load_word2vec_format('word2vec/cbow_s50.txt')


if __name__ == '__main__':
    cbow = CBoW()
    result = cbow.get_similar('padaria')
    print(result)