import argparse
import os

from user import User, EmpUser, CustomEmpUser, WFCUser, BayesUser, ChiUser
import twitterhandler
from emoji2vec import Emoji2Vec
import chisquaredmodel
import bayesmodel
import sys
import json
from metricsanalyzer import Metrics

ALGORITHMS = {x.__name__.replace("User", "").lower(): lambda u, a=eval(f"{x.__name__}"): a(u)
              for x in User.__subclasses__()}


def analyze_users(num_of_tweets=2000, force_new_tweets=False, emojis=False):
    users = []
    with open("data/handles.json", "r") as file:
        people = json.load(file)
    for algorithm in ALGORITHMS:
        for name in people:
            person = ALGORITHMS[algorithm](name)
            if person.load_user_data():
                users.append(person)
            # if isinstance(person, ChiUser) or isinstance(person, BayesUser):
            #     if person.load_user_data():
            #         users.append(person)
            # else:
            #     users.append(analyze_user(person, num_of_tweets, force_new_tweets, emojis))
    # Metrics.analyze_users(users)
    for person in users:
        Emoji2Vec.emojis_for(person)


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
        Emoji2Vec.emojis_for(person)

    # Metrics.analyze_user(person)
    return person


def calc():
    for algorithm in ALGORITHMS:
        Metrics.calculate_statistics(type(ALGORITHMS[algorithm]("adamdoestw")))


def gather_known_users():
    known_users = os.listdir("data/people/")
    with open("data/handles.json", "w") as file:
        json.dump(known_users, file)


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
                        default="chi",
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
    parser.add_argument("-m",
                        "--metrics",
                        dest="metrics",
                        action="store_true",
                        help="Gather metrics for known users")

    args = parser.parse_args()
    user = None
    if args.metrics:
        gather_known_users()
        analyze_users()
        calc()
    elif args.analyzer in ALGORITHMS:
        user = ALGORITHMS[args.analyzer](args.username)
        analyze_user(user, args.tweet_num, args.force, args.emojis)
