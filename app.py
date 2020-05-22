from flask import Flask, request, send_file
from flask_restplus import Resource, Api
import analyzeuser
from user import User, EmpUser, CustomEmpUser, WFCUser, BayesUser, ChiUser
import emoji2vector
import os
import getemojis


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
            if algorithm is not None and username is not None:
                if algorithm in "chi-squared":
                    person = ChiUser(username)
                if algorithm in "wfc":
                    person = WFCUser(username)
                if algorithm in "empath":
                    person = EmpUser(username)
                if algorithm in "bayes":
                    person = BayesUser(username)
                if algorithm in "custom":
                    person = CustomEmpUser(username)
                analyzeuser.analyze_user(person, num_tweets, new_tweets)
                top_interests = User.top_n_interests(person, num_interests)
                result = []
                for interest in top_interests:
                    data_point = {'name': interest, 'score': top_interests[interest]}
                    emoji = emoji2vector.find_closest_emoji(interest, 1)
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
            algorithm = algorithm.lower()
            if algorithm is not None and user1 is not None and user2 is not None:
                if algorithm in "chi-squared":
                    user1 = ChiUser(user1)
                    user2 = ChiUser(user2)
                if algorithm in "wfc":
                    user1 = WFCUser(user1)
                    user2 = WFCUser(user2)
                if algorithm in "empath":
                    user1 = EmpUser(user1)
                    user2 = EmpUser(user2)
                if algorithm in "bayes":
                    user1 = BayesUser(user1)
                    user2 = BayesUser(user2)
                if algorithm in "custom":
                    user1 = CustomEmpUser(user1)
                    user2 = CustomEmpUser(user2)
                analyzeuser.analyze_user(user1, num_tweets, new_tweets)
                analyzeuser.analyze_user(user2, num_tweets, new_tweets)
                similar_interests = User.find_similar_interests(user1, user2, num_interests)
                for interest in similar_interests:
                    score = similar_interests[interest]
                    similar_interests[interest] = {}
                    similar_interests[interest]['score'] = score
                    emoji = emoji2vector.find_closest_emoji(interest, 1)
                    if emoji is not None:
                        similar_interests[interest]['emoji'] = emoji[0][0]
                        similar_interests[interest]['emojiScore'] = emoji[0][1]
                return similar_interests
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
            return emoji2vector.find_closest_emoji(word, number)

    api.add_resource(UserDataRequest, '/user/')
    api.add_resource(UserComparisonRequest, '/compare/')
    api.add_resource(EmojiImageRequest, '/emojis/')
    api.add_resource(NearestEmojisRequest, '/closest/')

    return application


if __name__ == '__main__':
    app = create_app()
    app.run()
