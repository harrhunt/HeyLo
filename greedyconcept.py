import operator
import time
import jsonpickle
from collections import OrderedDict
import matplotlib.pyplot as plt
import networkx as nx
from treevis import draw_tree

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
        self.path = None


class InterestPath:

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.path = []
        self.seen = set()

    def append(self, node):
        self.path.append(node)
        node.path = self
        self.seen.add(node.word)


class InterestTreeNode:

    def __init__(self, word, relation=None, edge=None, score=None):
        self.word = word
        self.relation = relation
        self.edge = edge
        self.score = score
        self.tree = None
        self.parent = None
        self.children = []
        self.depth = 0


class InterestTreePathNode:

    def __init__(self, word, relation, edge, score, parent):
        self.word = word
        self.relation = relation
        self.edge = edge
        self.score = score
        self.parent = parent


class InterestTree:

    def __init__(self, start, end):
        self.start = start.word
        self.head = start
        self.end = end
        self.current = start
        self.path = []
        self.queue = []
        self.seen = set()
        self.all = [start]

    def add_edges(self, parent, words):
        for word in words:
            if word not in self.seen:
                self.seen.add(word)
                node = InterestTreeNode(word, words[word]["relation"], words[word]["edge"], words[word]["score"])
                node.parent = parent
                node.depth = parent.depth + 1
                parent.children.append(node)
                self.queue.append(node)
                if word == self.end:
                    self.current = node
                    self.mark_path()

        self.queue = sorted(self.queue, key=lambda key: key.score, reverse=True)

    def next(self):
        self.current = self.queue.pop(0)
        print(self.current.word)
        self.all.append(self.current)
        return self.current

    def mark_path(self):
        while self.current.parent is not None:
            self.path.insert(0, InterestTreePathNode(self.current.word, self.current.relation, self.current.edge,
                                                     self.current.score, self.current.parent.word))
            self.current = self.current.parent
            self.mark_path()


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


def a_star_path(start, end, tree=None):
    if tree is None:
        tree = InterestTree(start, end)
    words = get_terms_list(start.word)
    to_delete = []
    if start.word in words:
        del words[start.word]
    for word in words:
        if Word2Vec.contains(word):
            similarity = Word2Vec.similarity(end, word)
            words[word]["score"] = float(similarity)
        else:
            to_delete.append(word)
    for word in to_delete:
        del words[word]
    tree.add_edges(start, words)
    if end in words:
        tree.next()
        return tree
    else:
        # for item in tree.queue:
        #     print(f"depth: {item[1]}, word: {item[2].word}, score: {item[0]}")
        return a_star_path(tree.next(), end, tree)


if __name__ == '__main__':
    # data = find_path("football", "sewing")
    data = a_star_path(InterestTreeNode("death"), "unicorns")
    # print(data.path)
    with open(f"data/paths/{data.start}-{data.end}.json", "w") as file:
        file.write(jsonpickle.encode(data.path))
    # with open("tree.json", "w") as file:
    #     file.write(jsonpickle.encode(data))
    draw_tree(data)
