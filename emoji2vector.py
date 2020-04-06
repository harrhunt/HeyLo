import re
import unicodedata
import gensim
from csv import reader
from gensim import downloader
import numpy as np
from gensim.models import KeyedVectors
import getemojis


def get_vector(words):
    vectors = []
    words = words.split('-')
    for word in words:
        if word in word2vec_model300.vocab:
            vectors.append(word2vec_model300.word_vec(word))

    average = np.average(vectors, 0)
    return average


def train_emoji_vectors():
    with open("data/emojis/emoji_df.csv", mode="r", encoding="utf-8", newline="") as file:
        lines = reader(file)

        codes = []

        for emoji in lines:
            if ":" not in emoji[1] and "," not in emoji[1]:
                clean = re.sub(r"[^a-zA-Z0-9\s-]+", "", emoji[1])
                lower = clean.lower()
                emoji = lower.split()
                emoji = '-'.join(emoji)
                codes.append(emoji)

    getemojis.get_emojis(codes)
    emoji_vectors = {}
    for code in codes:
        vector = get_vector(code)
        if isinstance(vector, np.ndarray):
            emoji_vectors[code] = get_vector(code)

    data = [f"{len(emoji_vectors)} 300"]
    for emoji in emoji_vectors:
        numbers = " ".join(str(number) for number in np.nditer(emoji_vectors[emoji]))
        line = f"{emoji} {numbers}"
        data.append(line)
    text = "\n".join(data)
    with open("data/emojis/emoji_vector_model.txt", "w") as file:
        file.write(text)


def find_closest_emoji(word, num):
    if word in word2vec_model300.vocab:
        vector = word2vec_model300.word_vec(word)
        return emoji_vector_model.similar_by_vector(vector, topn=num)
    else:
        return None


def get_distances(words):
    distances = []
    word_pairs = []
    good_words = []
    for word in words:
        if word in word2vec_model300.vocab:
            good_words.append(word)
    for word1 in good_words:
        for word2 in good_words:
            pair = {word1, word2}
            if pair not in word_pairs and len(pair) == 2:
                word_pairs.append(pair)
    for pair in word_pairs:
        distances.append(word2vec_model300.similarity(pair.pop(), pair.pop()))
    return distances


word2vec_model300 = downloader.load('word2vec-google-news-300')
train_emoji_vectors()
emoji_vector_model = KeyedVectors.load_word2vec_format("data/emojis/emoji_vector_model.txt")
