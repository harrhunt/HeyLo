import json
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import random
from cnrelated import get_related
from os import listdir, remove

STOPWORDS = set(stopwords.words('english'))


def get_random_relations():
    with open("data/1400_words.json", "r") as file:
        words = json.load(file)
    list_of_relations = []
    for word in words:
        relations = get_related(word)
        edges = list(relations.keys())
        if len(edges) > 0:
            edge = ""
            word_synset = wn.synsets(word)
            count = 0
            skip = False
            previous_edge = ""
            while True:
                if len(edges) <= 0:
                    skip = True
                    break
                edge = random.choice(edges)
                edge_synset = wn.synsets(edge)
                if 3 <= len(edge_synset) <= 7 and edge_synset != word_synset and relations[edge]["relation"] != "Antonym" and relations[edge]["relation"] != "DistinctFrom":
                    break
                edges.remove(edge)
                if edge == previous_edge:
                    count += 1
                previous_edge = edge
                if count > 10:
                    skip = True
                    break
            if skip:
                continue
            if relations[edge]["start"] == word:
                list_of_relations.append((word, edge))
            else:
                list_of_relations.append((edge, word))
    print(len(list_of_relations))
    with open("data/1000_relations.json", "w") as file:
        json.dump(list_of_relations, file)


def pick_n_words(n=1000):
    with open("data/cleaned_words.json", "r") as file:
        cleaned = json.load(file)
    new_list = []
    for i in range(n):
        new_list.append(random.choice(cleaned))
    print(len(new_list))
    with open(f"data/{n}_words.json", "w") as file:
        json.dump(new_list, file)


def clean_dictionary():
    # Words must have the following attributes:
    # Not be a stopword
    # Be in wordnet
    # Have at least 3 WSP and at most 7 WSP
    with open("data/words_list.json", "r") as file:
        words = json.load(file)
    clean_list = []
    for word in words:
        if word not in STOPWORDS:
            synsets = wn.synsets(word)
            if 3 <= len(synsets) <= 7:
                clean_list.append(word)
    print(len(clean_list))
    with open("data/cleaned_words.json", "w") as file:
        json.dump(clean_list, file)


def filter_obscenities():
    with open("data/obscenities.json", "r") as file:
        obscenities = json.load(file)
    path = "data/comparisons/"
    files = listdir(path)
    for file in files:
        name = file.split(".")[0]
        words = name.split("-")
        for word in words:
            if word in obscenities:
                print(file)
                remove(f"{path}{file}")
                break


if __name__ == '__main__':
    # clean_dictionary()
    # pick_n_words(1400)
    # get_random_relations()
    filter_obscenities()
    # word1 = wn.synsets("office")
    # word2 = wn.synsets("offices")
    # print(word1, word2)
    # if word1 == word2:
    #     print("true")
    # new_list = []
    # for i in range(1000):
    #     new_list.append(random.choice(words))

    # with open("data/1000_words.json", "w") as file:
    #     json.dump(new_list, file)
