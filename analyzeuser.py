import argparse
from empuser import EmpUser
from customempuser import CustomEmpUser
from wfcuser import WFCUser
from chiuser import ChiUser
from bayesuser import BayesUser
import twitterhandler
from getemojis import get_emojis
import chisquaredmodel
import bayesmodel
import sys
import json
from metricsanalyzer import Metrics


def analyze_users(num_of_tweets=2000, force_new_tweets=False, emojis=False):
    users = []
    with open("data/handles.json", "r") as file:
        people = json.load(file)
    for name in people:
        person = ChiUser(name)
        tweets = None

        # Check for successful load of user data
        if not person.load_user_data():
            force_new_tweets = True
        elif len(person.tweets) <= 0:
            force_new_tweets = True

        # Check if we are forcing the system to get new tweets
        if force_new_tweets:
            if num_of_tweets > 0:
                print(f"Grabbing tweets for {person.username}")
                tweets = twitterhandler.get_tweets(person.username, num_of_tweets)

        # Do the analysis
        print(f"Analyzing tweets for {person.username}")
        person.find_words(tweets)
        # user.print_words()
        if isinstance(person, ChiUser):
            print(f"Working statistical analysis for {person.username}")
            chisquaredmodel.add_user(person)
            chisquaredmodel.calculate_user(person)
        elif isinstance(person, BayesUser):
            print(f"Working statistical analysis for {person.username}")
            bayesmodel.add_user(person)
            bayesmodel.calculate_user(person)
        else:
            person.add_interests(person.words)
        # user.print_interests()
        if emojis:
            print(f"Getting emojis for {person.username}")
            get_emojis(person)
        users.append(person)
    Metrics.analyze_users(users)


def analyze_user(person, num_of_tweets=2000, force_new_tweets=False, emojis=False):
    tweets = None

    # Check for successful load of user data
    if not person.load_user_data():
        force_new_tweets = True
    elif len(person.tweets) <= 0:
        force_new_tweets = True

    # Check if we are forcing the system to get new tweets
    if force_new_tweets:
        if num_of_tweets > 0:
            print(f"Grabbing tweets for {person.username}")
            tweets = twitterhandler.get_tweets(person.username, num_of_tweets)

    # Do the analysis
    print(f"Analyzing tweets for {person.username}")
    person.find_words(tweets)
    # user.print_words()
    if isinstance(person, ChiUser):
        print(f"Working statistical analysis for {person.username}")
        chisquaredmodel.add_user(person)
        chisquaredmodel.calculate_user(person)
    elif isinstance(person, BayesUser):
        print(f"Working statistical analysis for {person.username}")
        bayesmodel.add_user(person)
        bayesmodel.calculate_user(person)
    else:
        person.add_interests(person.words)
    # user.print_interests()
    if emojis:
        print(f"Getting emojis for {person.username}")
        get_emojis(person)

    # Metrics.analyze_user(person)
    return person


def calc():
    Metrics.calculate_statistics(type(ChiUser("adamdoestw")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="analyzeUser",
                                     description="Analyze the given Twitter user")

    parser.add_argument("username",
                        type=str,
                        help="The username of the Twitter user to analyze")
    parser.add_argument("tweet_num",
                        type=int,
                        nargs="?",
                        default=2000,
                        help="The number of Tweets to collect and analyze")
    parser.add_argument("-a",
                        "--analyzer",
                        action="store",
                        type=str,
                        nargs="?",
                        default="chi-squared",
                        const="bayes",
                        help="Use the empath version of interest extraction (default: Word Frequency Counter analyzer)")
    parser.add_argument("-f",
                        "--force-get-tweets",
                        dest="force",
                        action="store_true",
                        help="Force the system to retrieve new tweets")
    parser.add_argument("-e",
                        "--emojis",
                        dest="emojis",
                        action="store_true",
                        help="Get emojis for the analyzed user")

    args = parser.parse_args()
    user = None
    if args.analyzer == "empath":
        user = EmpUser(args.username)
    elif args.analyzer == "wfc":
        user = WFCUser(args.username)
    elif args.analyzer == "bayes":
        user = BayesUser(args.username)
    elif args.analyzer == "custom":
        user = CustomEmpUser(args.username)
    else:
        user = ChiUser(args.username)

    analyze_user(user, args.tweet_num, args.force, args.emojis)
