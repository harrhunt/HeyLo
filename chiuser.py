import operator

from user import User
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import corpus
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer


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
