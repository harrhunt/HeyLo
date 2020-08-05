import operator
import time
import jsonpickle
from collections import OrderedDict

import requests
from nltk.corpus import stopwords
from word2vec import Word2Vec
from empath import Empath


class InterestNode:

    def __init__(self, word, relation, edge, score):
        self.word = word
        self.relation = relation
        self.edge = edge
        self.score = score


class InterestPath:

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.path = []
        self.seen = set()

    def append(self, node):
        self.path.append(node)
        self.seen.add(node.word)


def get_terms_list(word):
    stop = stopwords.words("english")

    obj = requests.get(f"http://api.conceptnet.io/c/en/{word}?limit=600")
    # Add the word itself to the list
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return get_terms_list(word)
    else:
        obj = obj.json()
        obj_list = {}
        # Iterate through the edges of the word...
        for i, edges in enumerate(obj["edges"]):
            # If it's english proceed...
            if "language" in obj["edges"][i]["start"] and obj["edges"][i]["start"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["start"]["term"]
                term = edge.split('/')[-1]
                relation = obj["edges"][i]["rel"]["label"]
                # Add the reformatted term if it isn't already in the list
                if term not in obj_list and term not in stop:
                    obj_list[term] = {"relation": relation, "edge": "start"}
            if "language" in obj["edges"][i]["end"] and obj["edges"][i]["end"]["language"] == "en":
                # Reformat the term to be snake case (I don't remember why but I know it was for a reason)
                edge = obj["edges"][i]["end"]["term"]
                term = edge.split('/')[-1]
                relation = obj["edges"][i]["rel"]["label"]
                # Add the reformatted term if it isn't already in the list
                if term not in obj_list and term not in stop:
                    obj_list[term] = {"relation": relation, "edge": "end"}
        return obj_list


def get_relatedness(word1, word2):
    obj = requests.get(f"http://api.conceptnet.io/relatedness?node1=/c/en/{word1}&node2=/c/en/{word2}")
    # Add the word itself to the list
    if obj.status_code != 200:
        print(f"Sleeping for one minute because status code is: {obj.status_code}")
        time.sleep(60)
        return get_relatedness(word1, word2)
    else:
        return obj.json()["value"]


def find_path(start, end, path=None):
    if path is None:
        path = InterestPath(start, end)
    words = get_terms_list(start)
    similars = {}
    if start in words:
        del words[start]
    for word in path.seen:
        if word in words:
            del words[word]
    for word in words:
        if Word2Vec.contains(word):
            similarity = Word2Vec.similarity(end, word)
            similars[word] = float(similarity)
        # similarity = get_relatedness(end, word)
        # similars[word] = float(similarity)
    if len(similars) == 0:
        return find_path(path.path[-2].word, end, path)
    else:
        if end in words:
            path.append(InterestNode(end, words[end]["relation"], words[end]["edge"], similars[end]))
            print(end)
            return path
        else:
            max_key = max(similars.items(), key=operator.itemgetter(1))[0]
            path.append(InterestNode(max_key, words[max_key]["relation"], words[max_key]["edge"], similars[max_key]))
            print(max_key)
            return find_path(max_key, end, path)


if __name__ == '__main__':
    data = find_path("defense_attorney", "computer")
    print(data)
    with open("path.json", "w") as file:
        file.write(jsonpickle.encode(data))
