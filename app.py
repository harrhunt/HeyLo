import inspect

from flask import Flask, request, send_file
from flask_restplus import Resource, Api
import analyzeuser
from user import *
from emoji2vec import Emoji2Vec
import os
import getemojis
from usercomparer import UserComparer

ALGORITHMS = {x.__name__.replace("User", "").lower(): lambda u, a=eval(f"{x.__name__}"): a(u)
              for x in User.__subclasses__()}
COMPARISONS = {x[0].lower(): lambda u1, u2, n=10, c=eval(f"UserComparer.{x[0]}"): c(u1, u2, n) for x in
               inspect.getmembers(UserComparer, predicate=inspect.isfunction) if
               {'user1', 'user2'}.issubset(set(x[1].__code__.co_varnames)) and
               x[1].__code__.co_argcount == 3 and "__" not in x[0]}


def create_app():
    application = Flask(__name__)
    api = Api(application)

    @application.route('/')
    def hello_world():
        return 'Hello World!'

    class UserDataRequest(Resource):
        def post(self):
            settings = request.get_json()
            print(settings)
            algorithm = settings['algorithm']
            username = settings['username']
            new_tweets = settings['newTweets']
            num_tweets = settings['numTweets']
            num_interests = settings['numInterests']
            algorithm = algorithm.lower()
            if algorithm is not None and username is not None and algorithm in ALGORITHMS:
                person = ALGORITHMS[algorithm](username)
                analyzeuser.analyze_user(person, num_tweets, new_tweets)
                top_interests = UserComparer.top_interests(person, num_interests)
                result = []
                for interest in top_interests:
                    data_point = {'name': interest, 'score': top_interests[interest]}
                    emoji = Emoji2Vec.nearest(interest, 1)
                    if emoji is not None:
                        data_point['emoji'] = emoji[0][0]
                        data_point['emojiScore'] = emoji[0][1]
                    result.append(data_point)

                return result
            return "<h1>Error</h1>"

    class UserComparisonRequest(Resource):
        def post(self):
            settings = request.get_json()
            algorithm = settings['algorithm']
            user1 = settings['user1']
            user2 = settings['user2']
            new_tweets = settings['newTweets']
            num_tweets = settings['numTweets']
            num_interests = settings['numInterests']
            comparer = settings["comparer"]
            algorithm = algorithm.lower()
            if algorithm is not None and user1 is not None and user2 is not None:
                user1 = ALGORITHMS[algorithm](user1)
                user2 = ALGORITHMS[algorithm](user2)
                analyzeuser.analyze_user(user1, num_tweets, new_tweets)
                analyzeuser.analyze_user(user2, num_tweets, new_tweets)
                similar_interests = COMPARISONS[comparer](user1, user2, num_interests)
                results = {}
                for interest in similar_interests:
                    pair = None
                    key = None
                    if "-" in interest:
                        cut = interest.split("-")
                        key = cut[1]
                        pair = cut[0]
                    else:
                        key = interest
                    results[key] = {}
                    score = similar_interests[interest]
                    results[key]['score'] = score
                    if pair is not None:
                        results[key]['pair'] = pair
                    emoji = Emoji2Vec.nearest(key, 1)
                    if emoji is not None:
                        results[key]['emoji'] = emoji[0][0]
                        results[key]['emojiScore'] = emoji[0][1]
                return results
            return "<h1>Error</h1>"

    class EmojiImageRequest(Resource):
        def post(self):
            settings = request.get_json()
            emoji = settings['emoji']
            filename = os.path.dirname(f"data/emojis/{emoji}.png")
            if os.path.exists(filename):
                return send_file(f"data/emojis/{emoji}.png", mimetype="image/png")
            else:
                getemojis.get_emojis(emoji)
                return send_file(f"data/emojis/{emoji}.png", mimetype="image/png")

    class NearestEmojisRequest(Resource):
        def post(self):
            settings = request.get_json()
            word = settings['word']
            number = settings['number']
            return Emoji2Vec.nearest(word, number)

    api.add_resource(UserDataRequest, '/user/')
    api.add_resource(UserComparisonRequest, '/compare/')
    api.add_resource(EmojiImageRequest, '/emojis/')
    api.add_resource(NearestEmojisRequest, '/closest/')

    return application


if __name__ == '__main__':
    app = create_app()
    app.run()
