from tweepy import API
from tweepy import OAuthHandler
from tweepy import Cursor


import credential as cred


def get_tweets(user, num_of_tweets):

    auth = OAuthHandler(cred.CONSUMER_KEY, cred.CONSUMER_SECRET)
    auth.set_access_token(cred.ACCESS_TOKEN, cred.ACCESS_SECRET)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    text = []
    for status in Cursor(api.user_timeline, id=user, tweet_mode="extended").items(num_of_tweets):
        # print(status.full_text)
        text.append(status.full_text)

    return text



