import re
import unicodedata
from csv import reader
import numpy as np
import getemojis
from word2vec import Word2Vec
from gensim.models import KeyedVectors


class Emoji2Vec:
    model = KeyedVectors.load_word2vec_format("data/emojis/emoji_vector_model")

    @classmethod
    def train_emoji_vectors(cls):
        with open("data/emojis/emoji_df.csv", mode="r", encoding="utf-8", newline="") as file:
            lines = reader(file)
            emojis = []
            for emoji in lines:
                if ":" not in emoji[1] and "," not in emoji[1]:
                    clean = re.sub(r"[^a-zA-Z0-9\s-]+", "", emoji[1])
                    lowered = clean.lower()
                    emojis.append(lowered)
        emoji_vectors = {}
        for emoji in emojis:
            vectors = Word2Vec.vectors(emoji)
            vector = np.average(vectors, 0)
            if isinstance(vector, np.ndarray):
                emoji_vectors[emoji] = Word2Vec.vector(emoji)

        data = [f"{len(emoji_vectors)} 300"]
        for emoji in emoji_vectors:
            numbers = " ".join(str(number) for number in np.nditer(emoji_vectors[emoji]))
            line = f"{emoji} {numbers}"
            data.append(line)
        text = "\n".join(data)
        with open("data/emojis/emoji_vector_model", "w") as file:
            file.write(text)

    @classmethod
    def nearest(cls, word, num):
        if Word2Vec.contains(word):
            vector = Word2Vec.vector(word)
            return cls.model.similar_by_vector(vector, topn=num)
        else:
            return None


Emoji2Vec.train_emoji_vectors()
