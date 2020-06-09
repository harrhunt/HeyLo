import json
import re
import numpy as np
from word2vec import Word2Vec
from gensim.models import KeyedVectors


class Emoji2Vec:
    model = KeyedVectors.load_word2vec_format("data/emojis/emoji_vector_model")

    @classmethod
    def train_emoji_vectors(cls):
        emojis = []
        with open("data/emojis.json", "r") as file:
            data = json.load(file)
        for emoji in data:
            spaced = re.sub(r"-+", " ", emoji)
            lowered = spaced.lower()
            emojis.append(lowered)
        emoji_vectors = {}
        for emoji in emojis:
            vectors = Word2Vec.vectors(emoji)
            # TODO: Change average to add instead for next paper
            vector = np.average(vectors, 0)
            if isinstance(vector, np.ndarray):
                emoji_vectors[re.sub(r"\s+", "-", emoji)] = vector

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

    @classmethod
    def emojis_for(cls, user):
        emojis = {}
        for interest in user.interests:
            emoji = Emoji2Vec.nearest(interest, 1)
            if emoji is not None:
                emojis[interest] = {"emoji": emoji[0][0], "score": emoji[0][1]}
        user.add_emojis(emojis)


if __name__ == '__main__':
    Emoji2Vec.train_emoji_vectors()
