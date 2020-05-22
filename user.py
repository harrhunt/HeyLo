import operator
from abc import ABC, abstractmethod
from collections import OrderedDict
import re
import os
import json
from empath import Empath
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import corpus
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer


class User(ABC):
    username = ""
    words = OrderedDict()
    interests = OrderedDict()
    tweets = ""
    emojis = OrderedDict()
    metrics = {}

    def __init__(self, username):
        self.username = username

    @staticmethod
    def get_top_n(data, num):
        top = {}
        data_copy = data.copy()
        for i in range(num):
            if len(data_copy) > 0:
                max_key = max(data_copy.items(), key=operator.itemgetter(1))[0]
                top[max_key] = data_copy[max_key]
                del data_copy[max_key]
        return top

    @staticmethod
    def find_similar_interests(user1, user2, num_interests=10):
        interests_1 = {}
        interests_2 = {}
        max_val_1 = list(User.top_n_interests(user1, 1).values())[0]
        max_val_2 = list(User.top_n_interests(user2, 1).values())[0]
        common_interests = {}

        for interest in user1.interests:
            interests_1[interest] = (user1.interests[interest] / max_val_1)
        for interest in user2.interests:
            interests_2[interest] = (user2.interests[interest] / max_val_2)
        for interest in interests_1:
            if interest in interests_2:
                common_interests[interest] = interests_1[interest] * interests_2[interest]
        # Select the top n interests
        return User.get_top_n(common_interests, num_interests)

    @staticmethod
    def top_n_interests(user1, num_interests=10):
        interests = {}
        for interest in user1.interests:
            value = user1.interests[interest]
            interests[interest] = value
        # Select the top n interests
        return User.get_top_n(interests, num_interests)

    def preprocess_data(self, text):
        if text is not None:
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

    def find_words(self, text=None):
        # Clean the text, process the data in subclasses, then do postprocess stuff
        self.postprocess_data(self.process_data(self.preprocess_data(text)))

    def postprocess_data(self, raw_data):
        # Sort by score highest to lowest, Store, and Save the interests
        sorted_data = OrderedDict(sorted(raw_data.items(), key=lambda x: x[1], reverse=True))
        self.words = sorted_data
        self.interests = sorted_data
        self.save_user_data()

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

    def add_interests(self, interests):
        sorted_interests = OrderedDict(sorted(interests.items(), key=lambda x: x[1], reverse=True))
        self.interests = sorted_interests
        self.save_user_data()

    def add_emojis(self, emojis):
        sorted_emojis = OrderedDict(sorted(emojis.items(), key=lambda x: x[1], reverse=True))
        self.emojis = sorted_emojis
        self.save_user_data()

    def save_user_data(self):
        # Create object to store in JSON
        user_obj = {"username": self.username, "words": self.words,
                    "emojis": self.emojis, "interests": self.interests}
        tweets = {"tweets": self.tweets}
        # Try to make the directory first if it doesn't already exist
        directory = os.path.dirname(
            "data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json")
        tweets_dir = os.path.dirname("data/people/" + self.username + "/" + self.username + ".tweets.json")
        try:
            os.makedirs(directory)
        except IOError as err:
            err
        try:
            os.makedirs(tweets_dir)
        except IOError as err:
            err
        # Save the user interests to a JSON file
        if self.words is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + "." + type(self).__name__ + ".json",
                          "w") as file:
                    json.dump(user_obj, file)
            except IOError as err:
                err
        if self.tweets is not None:
            try:
                with open("data/people/" + self.username + "/" + self.username + ".tweets.json",
                          "w") as file:
                    json.dump(tweets, file)
            except IOError as err:
                err

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
        if 'usersname' in user_obj:
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
        if 'emojis' in user_obj:
            self.emojis = user_obj["emojis"]
        return successful


class EmpUser(User):
    emp = Empath()

    def __init__(self, username):
        super().__init__(username)

    def process_data(self, clean):
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
