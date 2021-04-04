import glob
import operator
from abc import ABC, abstractmethod
from collections import OrderedDict
import re
import os
import json
from zipfile import ZipFile
from usercomparer import UserComparer

from empath import Empath
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk import corpus
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from word2vec import Word2Vec
from wsp import WSG, WSP, WSPComparer
from oxford import get_all_coarse_defs
import numpy as np


class User(ABC):
    username = ""
    words = OrderedDict()
    interests = OrderedDict()
    tweets = ""
    emojis = OrderedDict()
    metrics = {}
    bag_of_tweets = []

    def __init__(self, username):
        self.username = username

    def preprocess_data(self, text):
        if text is not None:
            self.bag_of_tweets = text
            self.tweets = " ".join(text)
        elif self.tweets is None:
            print("No tweets to process")
            return

        # Clean the text saving only letters and white space
        http_free = re.sub(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            " ", self.tweets)
        url_free = re.sub(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", " ",
                          http_free)
        return re.sub(r"[^a-zA-Z\s]+", " ", url_free)

    @abstractmethod
    def process_data(self, clean):
        pass

    def postprocess_data(self, raw_data):
        # Sort by score highest to lowest, Store, and Save the interests
        sorted_data = OrderedDict(sorted(raw_data.items(), key=lambda x: x[1], reverse=True))
        self.words = sorted_data
        self.interests = sorted_data
        self.save_user_data()

    def find_words(self, text=None):
        # Clean the text, process the data in subclasses, then do postprocess stuff
        self.postprocess_data(self.process_data(self.preprocess_data(text)))

    def print_words(self):
        # Print the user's interests
        for word in self.words:
            if self.words[word] > 0:
                print(f"{word}: {self.words[word]}")

    def print_interests(self):
        # Print the user's interests
        for interest in self.interests:
            if self.interests[interest] > 0:
                print(f"{interest}: {self.interests[interest]}")

    def disambiguate_interest(self, interest):
        # for interest in UserComparer.top_interests(self, num_interests=5):
        #     print(f"INTEREST HERE ----->>>>>> {interest}")
        interest_total_vector = np.zeros(shape=(300,), dtype=float)
        for tweet in self.bag_of_tweets:
            if interest in word_tokenize(tweet):
                http_free = re.sub(
                    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                    " ", tweet)
                url_free = re.sub(
                    r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", " ",
                    http_free)
                clean = re.sub(r"[^a-zA-Z\s]+", " ", url_free)
                tweet_total_vector = Word2Vec.total_vector(clean)
                interest_total_vector = np.add(tweet_total_vector, interest_total_vector)
        interest_wsg = WSG(interest)
        definitions = get_all_coarse_defs(interest)
        if isinstance(definitions, int):
            print(f"MISSING FROM OXFORD DICTIONARY: {interest}")
            return None
        data = WSPComparer.group_by_closest_definition(interest_wsg, definitions)
        best = [-1, None, None]
        Word2Vec.add_vector(f"{interest}_interest_vec", interest_total_vector)
        for wsp in interest_wsg.wsp_list:
            Word2Vec.add_vector(f"{wsp.word}_wsp", wsp.get_total_vector())
            score = Word2Vec.similarity(f"{interest}_interest_vec", f"{wsp.word}_wsp")
            if score > best[0]:
                best[0] = score
                best[1] = wsp
                best[2] = wsp.oxdef
        print(best[0], best[2])
        for definition in data:
            print("\n")
            print(definition)
        return best[2]

    def add_interests(self, interests):
        sorted_interests = OrderedDict(sorted(interests.items(), key=lambda x: x[1], reverse=True))
        self.interests = sorted_interests
        self.save_user_data()

    def add_emojis(self, emojis):
        sorted_emojis = OrderedDict(sorted(emojis.items(), key=lambda x: operator.getitem(x[1], "score"), reverse=True))
        self.emojis = sorted_emojis
        self.save_user_data()

    def save_user_data(self):
        # Create object to store in JSON
        user_obj = {"username": self.username, "words": self.words,
                    "emojis": self.emojis, "interests": self.interests}
        tweets = {"tweets": self.tweets, "bag_of_tweets": self.bag_of_tweets}
        # Try to make the directory first if it doesn't already exist
        directory = os.path.dirname(
            "data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json")
        tweets_dir = os.path.dirname("data/people/" + self.username + "/" + self.username + ".tweets.json")
        try:
            os.makedirs(directory)
        except IOError as err:
            pass
        try:
            os.makedirs(tweets_dir)
        except IOError as err:
            pass
        # Save the user interests to a JSON file
        if self.words is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json",
                          "w") as file:
                    json.dump(user_obj, file)
            except IOError as err:
                pass
        if self.tweets is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + ".tweets.json",
                          "w") as file:
                    json.dump(tweets, file)
            except IOError as err:
                pass

    def load_user_data(self):

        successful = False

        # Load the interests JSON and set to self.interests
        user_obj = {}
        tweets = {}
        try:
            with open("data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json",
                      "r") as data:
                user_obj = json.load(data)
            successful = True
        except IOError:
            successful = False
        try:
            with open("data/people/" + self.username + "/" + self.username + ".tweets.json", "r") as tweet_data:
                tweets = json.load(tweet_data)
            successful = True
        except IOError:
            successful = False

        # Assign values from load to fields
        if 'username' in user_obj:
            self.username = user_obj["username"]
        if 'words' in user_obj:
            self.words = user_obj["words"]
        if 'interests' in user_obj:
            self.interests = user_obj["interests"]
        if 'tweets' in tweets:
            print("GOT THE TWEETS")
            self.tweets = tweets["tweets"]
        elif 'tweets' in user_obj:
            print("GOT THE TWEETS")
            self.tweets = user_obj["tweets"]
        else:
            print("There seem to be no tweets")
        if 'bag_of_tweets' in tweets:
            print("Has Bag of Tweets")
            self.bag_of_tweets = tweets["bag_of_tweets"]
        elif 'bag_of_tweets' in user_obj:
            print("Has Bag of Tweets")
            self.bag_of_tweets = tweets["bag_of_tweets"]
        if 'emojis' in user_obj:
            self.emojis = user_obj["emojis"]
        return successful


class EmpUser(User):
    emp = Empath()

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        files = glob.glob('../XRCC_RestAPI/venv/Lib/site-packages/empath/data/user/*.empath')
        if len(files) > 0:
            # Iterate over the list of filepaths & remove each file.
            for file in files:
                try:
                    os.remove(file)
                except:
                    print("Error while deleting file : ", file)
        try:
            with open("data/original.json", "r") as file:
                topics = json.load(file)
            raw_data = self.emp.analyze(clean, categories=topics["topics"])

        # Otherwise, run empath without topics filter
        except IOError as err:
            print(err, "\r\nUsing all categories")
            raw_data = self.emp.analyze(clean)

        # Delete interests generated if they have a hit score of 0
        keys_to_delete = []
        for key in raw_data:
            if raw_data[key] <= 0:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del raw_data[key]

        return raw_data


class CustomEmpUser(User):
    emp = Empath()

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        files = glob.glob('../XRCC_RestAPI/venv/Lib/site-packages/empath/data/user/*.empath')
        if len(files) <= 0:
            with ZipFile('../XRCC_RestAPI/venv/Lib/site-packages/empath/data/user/user.zip', 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall('../XRCC_RestAPI/venv/Lib/site-packages/empath/data/user')
        # Try to get topic list if it exists
        try:
            with open("data/topics.json", "r") as file:
                topics = json.load(file)
            raw_data = self.emp.analyze(clean, categories=topics["topics"])

        # Otherwise, run empath without topics filter
        except IOError as err:
            print(err, "\r\nUsing all categories")
            raw_data = self.emp.analyze(clean)

        # Delete interests generated if they have a hit score of 0
        keys_to_delete = []
        for key in raw_data:
            if raw_data[key] <= 0:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del raw_data[key]

        return raw_data


class WFCUser(User):

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        lemmatizer = WordNetLemmatizer()

        # Tag words with part of speech
        words = pos_tag(word_tokenize(clean))

        # Get stop words
        stop = stopwords.words("english")

        # Get english words
        english = set(corpus.words.words())

        # Count the frequency of each word that is english, a verb or noun, and not a stop word
        raw_data = {}
        for word in words:
            lower_word = word[0].lower()
            if lower_word not in stop:
                if lower_word in english and len(lower_word) > 2:
                    if "NN" in word[1] or "VB" in word[1]:
                        lemma_word = lemmatizer.lemmatize(lower_word)
                        if lemma_word not in raw_data:
                            raw_data[lemma_word] = 1
                        else:
                            raw_data[lemma_word] += 1

        # Select the top five interests
        # top5 = {}
        # for i in range(5):
        #     max_key = max(raw_data.items(), key=operator.itemgetter(1))[0]
        #     print(max_key)
        #     top5[max_key] = raw_data[max_key]
        #     del raw_data[max_key]

        # Delete interests generated if they have a hit score of 3 or less
        # keys_to_delete = []
        # for key in raw_data:
        #     if raw_data[key] <= 10:
        #         keys_to_delete.append(key)
        # for key in keys_to_delete:
        #     del raw_data[key]

        return raw_data


class BayesUser(User):

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        lemmatizer = WordNetLemmatizer()

        # Tag words with part of speech
        words = pos_tag(word_tokenize(clean))

        # Get stop words
        stop = stopwords.words("english")

        # Get english words
        english = set(corpus.words.words())

        # Count the frequency of each word that is english, a verb or noun, and not a stop word
        raw_data = {}
        for word in words:
            lower_word = word[0].lower()
            if lower_word not in stop:
                if lower_word in english and len(lower_word) > 2:
                    if "NN" in word[1] or "VB" in word[1]:
                        # lemma_word = lemmatizer.lemmatize(lower_word)
                        # Try passing in part of speech
                        if "NN" in word[1]:
                            lemma_word = lemmatizer.lemmatize(lower_word, 'n')
                        if "VB" in word[1]:
                            lemma_word = lemmatizer.lemmatize(lower_word, 'v')
                        if lemma_word not in raw_data:
                            raw_data[lemma_word] = 1
                        else:
                            raw_data[lemma_word] += 1

        # Select the top five interests
        # top5 = {}
        # for i in range(5):
        #     max_key = max(raw_data.items(), key=operator.itemgetter(1))[0]
        #     print(max_key)
        #     top5[max_key] = raw_data[max_key]
        #     del raw_data[max_key]

        # Delete interests generated if they have a hit score of 3 or less
        # keys_to_delete = []
        # for key in raw_data:
        #     if raw_data[key] <= 10:
        #         keys_to_delete.append(key)
        # for key in keys_to_delete:
        #     del raw_data[key]

        return raw_data


class ChiUser(User):

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
        lemmatizer = WordNetLemmatizer()

        # Tag words with part of speech
        words = pos_tag(word_tokenize(clean))

        # Get stop words
        stop = stopwords.words("english")

        # Get english words
        english = set(corpus.words.words())

        # Count the frequency of each word that is english, a verb or noun, and not a stop word
        raw_data = {}
        for word in words:
            lower_word = word[0].lower()
            if lower_word not in stop:
                if lower_word in english and len(lower_word) > 2:
                    if "NN" in word[1] or "VB" in word[1]:
                        # lemma_word = lemmatizer.lemmatize(lower_word)
                        # Try passing in part of speech
                        if "NN" in word[1]:
                            lemma_word = lemmatizer.lemmatize(lower_word, 'n')
                        if "VB" in word[1]:
                            lemma_word = lemmatizer.lemmatize(lower_word, 'v')
                        if lemma_word not in raw_data:
                            raw_data[lemma_word] = 1
                        else:
                            raw_data[lemma_word] += 1

        # Select the top five interests
        # top5 = {}
        # for i in range(5):
        #     max_key = max(raw_data.items(), key=operator.itemgetter(1))[0]
        #     print(max_key)
        #     top5[max_key] = raw_data[max_key]
        #     del raw_data[max_key]

        # Delete interests generated if they have a hit score of 3 or less
        # keys_to_delete = []
        # for key in raw_data:
        #     if raw_data[key] <= 10:
        #         keys_to_delete.append(key)
        # for key in keys_to_delete:
        #     del raw_data[key]

        return raw_data
