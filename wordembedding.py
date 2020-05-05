# -*- coding: utf-8 -*-
import os
from gensim.models import KeyedVectors


class WordEmbbeding(object):
    """Class to use the functions of WordEmbedding models."""
    model = None
    filename = None
    ideal_similarity = 0.0

    def __init__(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.join(dirname, 'data_embedding')
        binary_model_filename = os.path.join(dirname, self.filename + '.mbin')
        txt_model_filename = os.path.join(dirname, self.filename + '.txt')

        if os.path.isfile(binary_model_filename):
            self.model = KeyedVectors.load(binary_model_filename)
        else:
            self.model = KeyedVectors.load_word2vec_format(txt_model_filename)
            self.model.save(binary_model_filename)

    def get_similar(self, word, top_n=3):
        """This method returns the TOP_N most similar words.

        Args:
            word (str): Word about which you want to get similar ones.
            top_n (int): Quantity of the most similar words to be
                returned.

        Returns:
            list[str]: List of TOP_N most similar words.
        """
        try:
            most_similar = self.model.most_similar(word)
            top_similar = [
                x for (x, sim) in most_similar[:top_n]
                if sim > self.ideal_similarity
            ]
            return top_similar
        except KeyError:
            return []


class CBoW(WordEmbbeding):
    filename = 'cbow_s50'


if __name__ == '__main__':
    cbow = CBoW()
    result = cbow.get_similar('padaria')
    print(result)
    import pdb;pdb.set_trace()