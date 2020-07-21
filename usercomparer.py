import operator
from word2vec import Word2Vec
from math import sqrt

class UserComparer:

    @staticmethod
    def __top(data, num):
        top = {}
        data_copy = data.copy()
        for i in range(num):
            if len(data_copy) > 0:
                max_key = max(data_copy.items(), key=operator.itemgetter(1))[0]
                top[max_key] = data_copy[max_key]
                del data_copy[max_key]
        return top

    @staticmethod
    def __top_exclusive(data, num):
        top = {}
        data_copy = data.copy()
        exclusive = []
        while len(top.keys()) < num and len(data_copy) > 0:
            max_key = max(data_copy.items(), key=operator.itemgetter(1))[0]
            cut = max_key.split('-')
            if cut[0] not in exclusive and cut[1] not in exclusive:
                exclusive.extend(cut)
                top[max_key] = data_copy[max_key]
            del data_copy[max_key]
        return top

    @staticmethod
    def top_interests(user, num_interests=10):
        interests = {}
        for interest in user.interests:
            value = user.interests[interest]
            interests[interest] = value
        # Select the top n interests
        return UserComparer.__top(interests, num_interests)

    @staticmethod
    def same(user1, user2, num_interests=10):
        if len(user1.interests) <= 0 or len(user2.interests) <= 0:
            return {}
        interests_1 = {}
        interests_2 = {}
        max_val_1 = list(UserComparer.top_interests(user1, 1).values())[0]
        max_val_2 = list(UserComparer.top_interests(user2, 1).values())[0]
        results = {}

        for interest in user1.interests:
            interests_1[interest] = (user1.interests[interest] / max_val_1)
        for interest in user2.interests:
            interests_2[interest] = (user2.interests[interest] / max_val_2)
        for interest in interests_1:
            if interest in interests_2:
                results[interest] = interests_1[interest] * interests_2[interest]
        # Select the top n interests
        return UserComparer.__top(results, num_interests)

    @staticmethod
    def similar(user1, user2, num_interests=10):
        if len(user1.interests) <= 0 or len(user2.interests) <= 0:
            return {}
        interests_1 = UserComparer.top_interests(user1, 50)
        interests_2 = UserComparer.top_interests(user2, 50)
        max_val_1 = list(UserComparer.top_interests(user1, 1).values())[0]
        max_val_2 = list(UserComparer.top_interests(user2, 1).values())[0]
        paired_interests = set()
        results = {}

        for word1 in interests_1:
            interests_1[word1] = (user1.interests[word1] / max_val_1)
        for word2 in interests_2:
            interests_2[word2] = (user2.interests[word2] / max_val_2)
        for word1 in interests_1:
            for word2 in interests_2:
                paired_interests.add((word1, word2))

        for pair in paired_interests:
            if Word2Vec.contains(pair[0]) and Word2Vec.contains(pair[1]):
                similarity = Word2Vec.similarity(pair[0], pair[1])
                results[f"{pair[0]}-{pair[1]}"] = interests_1[pair[0]] * interests_2[pair[1]] * sqrt(similarity)
        # Select the top n interests
        return UserComparer.__top_exclusive(results, num_interests)
