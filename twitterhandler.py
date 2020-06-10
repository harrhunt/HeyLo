from tweepy import API
from tweepy import OAuthHandler
from tweepy import Cursor

import credentials as cred


def get_tweets(user, num_of_tweets):
    auth = OAuthHandler(cred.CONSUMER_KEY, cred.CONSUMER_SECRET)
    auth.set_access_token(cred.ACCESS_TOKEN, cred.ACCESS_SECRET)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    text = []
    for status in Cursor(api.user_timeline, id=user, tweet_mode="extended").items(num_of_tweets):
        tweet = ""
        print(f"{status.is_quote_status} and {status.retweeted}")
        if status.is_quote_status and status.retweeted:
            pass
        elif status.is_quote_status:
            if "retweeted_status" in status._json:
                tweet = status.full_text + " " + status.retweeted_status.full_text + " " + status.retweeted_status.quoted_status.full_text
            else:
                tweet = status.full_text + " " + status.quoted_status.full_text
        elif status.retweeted:
            tweet = status.retweeted_status.full_text
        else:
            tweet = status.full_text

        text.append(tweet)

    return text
