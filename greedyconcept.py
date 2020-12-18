import operator
import time
import jsonpickle
from collections import OrderedDict
import matplotlib.pyplot as plt
import networkx as nx
from treevis import draw_tree
from user import User
from usercomparer import UserComparer

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
        node.paths = self
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
        self.g = 0
        self.h = 0
        self.f = 0


class InterestTreePathNode:

    def __init__(self, word, relation, edge, score, parent):
        self.word = word
        self.relation = relation
        self.edge = edge
        self.score = score
        self.parent = parent


class InterestTree:

    def __init__(self, user1, user2, num_interests):
        self.user1 = user1
        self.user2 = user2
        self.start_words = list(UserComparer.top_interests(user1, num_interests).keys())
        print(self.start_words)
        self.start_nodes = [InterestTreeNode(word) for word in self.start_words if Word2Vec.contains(word)]
        self.end_words = list(UserComparer.top_interests(user2, num_interests).keys())
        print(self.end_words)
        self.end_nodes = [InterestTreeNode(word) for word in self.end_words if Word2Vec.contains(word)]
        self.current = None
        self.paths = []
        self.queue = []
        self.seen = {}
        self.all = []

    def add_edges(self, parent, words):
        for word in words:
            # if word not in self.seen:
            #     self.seen.add(word)
            node = InterestTreeNode(word, words[word]["relation"], words[word]["edge"], words[word]["score"])
            node.parent = parent
            node.depth = parent.depth + 1
            node.g = parent.g + (1 - Word2Vec.similarity(node.word, parent.word))
            node.h = 1 - node.score
            node.f = node.g + node.h
            parent.children.append(node)
            if word in self.seen:
                # print(f"{self.seen[word].f} vs {node.f}")
                if self.seen[word].f > node.f:
                    self.seen[word] = node
                    self.queue.append(node)
                else:
                    continue
            else:
                self.seen[word] = node
                self.queue.append(node)
            if word in self.end_words:
                print(f"The end word {node.word} has a score of f-score: {node.f}")
                print(f"{self.queue[:3]} : {self.queue[-1].word}")
                self.current = node
                self.all.append(self.current)
                self.mark_path()
                self.current = parent

    def next(self):
        self.queue = sorted(self.queue, key=lambda key: key.f)
        self.current = self.queue.pop(0)
        if self.current.word in self.seen:
            if self.current.f > self.seen[self.current.word].f:
                return self.next()
        print(self.current.word, self.current.f)
        self.all.append(self.current)
        return self.current

    def mark_path(self):
        self.paths.append([])
        while self.current.parent is not None:
            self.paths[-1].insert(0, InterestTreePathNode(self.current.word, self.current.relation, self.current.edge,
                                                          self.current.score, self.current.parent.word))
            self.current = self.current.parent

    def connect(self):
        self.queue = []
        self.all = []
        self.paths = []
        self.seen = {}
        for sword in self.start_words:
            if Word2Vec.contains(sword):
                best = -1
                similarity = 0
                for eword in self.end_words:
                    if Word2Vec.contains(eword):
                        similarity = Word2Vec.similarity(sword, eword)
                        print(sword, similarity, eword)
                        if similarity > best:
                            best = similarity
                node = InterestTreeNode(sword, score=similarity)
                node.g = 0
                node.h = 1 - best
                node.f = node.g + node.h
                self.queue.append(node)
        self.next()
        self.seen[self.current.word] = self.current
        self.a_star()

    def a_star(self):
        done = False
        while not done:
            words = get_terms_list(self.current.word)
            to_delete = []
            if self.current.word in words:
                del words[self.current.word]
            for word in words:
                if Word2Vec.contains(word):
                    if word in self.end_words:
                        print(f"An end showed up: {word}")
                    best = -1
                    for end in self.end_words:
                        if Word2Vec.contains(end):
                            similarity = Word2Vec.similarity(end, word)
                            if similarity > best:
                                words[word]["score"] = float(similarity)
                else:
                    to_delete.append(word)
            for word in to_delete:
                del words[word]
            self.add_edges(self.current, words)
            self.next()
            if self.current.word in self.end_words:
                print(f"The end word '{self.current.word}' popped; f-score: {self.current.f}")
                self.mark_path()
                done = True


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

# if __name__ == '__main__':
# data = find_path("football", "sewing")
# data = InterestTree()
# print(data.path)
# with open(f"data/paths/{data.start}-{data.end}.json", "w") as file:
#     file.write(jsonpickle.encode(data.path))
# with open("tree.json", "w") as file:
#     file.write(jsonpickle.encode(data))
# draw_tree(data)
