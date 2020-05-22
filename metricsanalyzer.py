import json
import os
from statistics import stdev, mean
from word2vec import Word2Vec
from cnrelated import count_types_of


class Metrics:
    data = {}

    @staticmethod
    def analyze_users(users):
        for user in users:
            print(f"getting metrics for {user.username}")
            Metrics.__analyze_user__(user)
        Metrics.__save_metrics__()

    @staticmethod
    def __analyze_user__(user):
        # Setup the metrics data object
        algorithm = type(user).__name__
        if algorithm not in Metrics.data:
            Metrics.data[algorithm] = {}
        if "people" not in Metrics.data[algorithm]:
            Metrics.data[algorithm]["people"] = {}
        if user.username not in Metrics.data[algorithm]["people"]:
            Metrics.data[algorithm]["people"][user.username] = {}

        # Get some basic info to start
        user_interests = list(user.get_top_n(user.interests, 5).keys())
        intra_user_distances = Word2Vec.get_distances(user_interests)

        # Calculate the following metrics:

        # Intra-User Variance
        if len(intra_user_distances) <= 0:
            Metrics.data[algorithm]["people"][user.username]["intra_user_variance"] = 0
        else:
            Metrics.data[algorithm]["people"][user.username]["intra_user_variance"] = sum(intra_user_distances) / len(
                intra_user_distances)

        # Inter-User Variance
        Metrics.data[algorithm]["people"][user.username]["words"] = user_interests

        # Specificity
        total_types_of = 0
        for interest in user_interests:
            total_types_of += count_types_of(interest)
        Metrics.data[algorithm]["people"][user.username]["specificity"] = 1 / (total_types_of + 1)

        # Save
        # Metrics.__save_metrics__()

    @staticmethod
    def calculate_statistics(algorithm_type):
        # Get things set up
        algorithm = algorithm_type.__name__
        average_intra_variance_distance = []
        if "intra_variance" not in Metrics.data[algorithm]:
            Metrics.data[algorithm]["intra_variance"] = {}
        if "specificity" not in Metrics.data[algorithm]:
            Metrics.data[algorithm]["specificity"] = {}

        # Calculate the following metrics:

        # Intra-Variance for an Algorithm
        for person in Metrics.data[algorithm]["people"]:
            average_intra_variance_distance.append(Metrics.data[algorithm]["people"][person]["intra_user_variance"])
        Metrics.data[algorithm]["intra_variance"]["mean"] = mean(average_intra_variance_distance)
        Metrics.data[algorithm]["intra_variance"]["stdev"] = stdev(average_intra_variance_distance)

        # Inter-Variance for an Algorithm
        total_number_interests = 0
        unique_words = set()
        for person in Metrics.data[algorithm]["people"]:
            total_number_interests += len(Metrics.data[algorithm]["people"][person]["words"])
            unique_words = unique_words.union(set(Metrics.data[algorithm]["people"][person]["words"]))
        Metrics.data[algorithm]["inter_variance"] = len(unique_words) / total_number_interests

        # Specificity for an Algorithm
        specificity_data = []
        for person in Metrics.data[algorithm]["people"]:
            specificity_data.append(Metrics.data[algorithm]["people"][person]["specificity"])
        Metrics.data[algorithm]["specificity"]["mean"] = mean(specificity_data)
        Metrics.data[algorithm]["specificity"]["stdev"] = stdev(specificity_data)

        # Save
        Metrics.__save_metrics__()

    @staticmethod
    def __save_metrics__():
        # Create object to store in JSON
        directory = os.path.dirname(
            "data/metrics/metrics.json")
        try:
            os.makedirs(directory)
        except IOError as err:
            err

        # Save the metrics to a JSON file
        if Metrics.data is not None:
            try:
                with open("data/metrics/metrics.json", "w") as file:
                    json.dump(Metrics.data, file)
            except IOError as err:
                print(err)

    @staticmethod
    def __load_metrics__():

        # Load the metrics JSON and set to Metrics.data
        try:
            with open("data/metrics/metrics.json", "r") as data:
                metrics = json.load(data)
        except IOError:
            metrics = {}

        # Assign values from load to fields
        Metrics.data = metrics


Metrics.__load_metrics__()
