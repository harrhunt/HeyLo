import operator
from abc import ABC, abstractmethod
from collections import OrderedDict
import re
import os
import json


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
