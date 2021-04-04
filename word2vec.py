from gensim import downloader
from nltk.corpus import stopwords
import numpy as np
import re

stop = stopwords.words('english')


class Word2Vec:
    model = downloader.load('word2vec-google-news-300')

    @classmethod
    def add_vector(cls, key, vector):
        cls.model.wv[key] = vector

    @classmethod
    def vector(cls, word):
        if word in cls.model.vocab:
            return cls.model.word_vec(word)

    @classmethod
    def vectors(cls, words):
        if not isinstance(words, list):
            words = str(words).split()
        vectors = []
        for word in words:
            if word in cls.model.vocab:
                vectors.append(cls.model.word_vec(word))
        return vectors

    @classmethod
    def total_vector(cls, words):
        to_remove = []
        if not isinstance(words, list) and not isinstance(words, set):
            clean = re.sub(r"[^A-z\s]+", " ", words)
            words = clean.split(" ")
        for word in words:
            if word in stop:
                to_remove.append(word)
        for word in to_remove:
            words.remove(word)
        total_vector = np.zeros(shape=(300,), dtype=float)
        for word in words:
            if cls.contains(word):
                total_vector = np.add(Word2Vec.vector(word), total_vector)
        return total_vector

    # @classmethod
    # def vector_similarity(cls, vector1, vector2):
    #     vector = np.ndarray(shape=(1,))
    #     similarity = cls.model.cosine_similarities(vector1, vector2)
    #     print(f"{similarity}")
    #     return similarity

    @classmethod
    def similarity(cls, word1, word2):
        return cls.model.similarity(word1, word2)

    @classmethod
    def get_distances(cls, words):
        distances = []
        word_pairs = []
        good_words = []
        for word in words:
            if word in cls.model.vocab:
                good_words.append(word)
        for word1 in good_words:
            for word2 in good_words:
                pair = {word1, word2}
                if pair not in word_pairs and len(pair) == 2:
                    word_pairs.append(pair)
        for pair in word_pairs:
            distances.append(cls.model.similarity(pair.pop(), pair.pop()))
        return distances

    @classmethod
    def contains(cls, word):
        return word in cls.model.vocab
