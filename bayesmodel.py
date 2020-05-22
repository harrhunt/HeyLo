from user import User
from user import BayesUser
import json
import os.path
from tweepy.error import TweepError


def create_data():
    with open('data/handles.OLD.json', 'r') as path:
        people = list(json.load(path))

    data = {'users': {}, 'words': {}, 'totalxy': 0}
    for person in people:
        print(person)
        person = BayesUser(person)
        if not person.load_user_data():
            continue
        person.find_words()
        if len(person.words) <= 0:
            continue

        # Initialize the user's fields
        data['users'][person.username] = {}
        data['users'][person.username]['words'] = person.words
        data['users'][person.username]['totaly'] = 0

        # Update the totals for each word the user has
        for word in person.words:
            data['users'][person.username]['totaly'] += person.words[word]
            if word not in data['words']:
                data['words'][word] = {}
            if 'totalx' not in data['words'][word]:
                data['words'][word]['totalx'] = person.words[word]
            else:
                data['words'][word]['totalx'] += person.words[word]

    return data


def compute_table_total():
    # Reset the model's total
    model['totalxy'] = 0

    # Make sure the total is the same for both x and y axis of the model
    word_total = 0
    user_total = 0
    for person in model['users']:
        user_total += model['users'][person]['totaly']
    for word in model['words']:
        word_total += model['words'][word]['totalx']
    print(f"User Total: {user_total}\nvs.\nWord Total: {word_total}")

    # If they are the same...
    if user_total == word_total:
        model['totalxy'] = user_total


def add_user(person):
    # If the person is not in the model...
    if person.username not in model['users']:
        # print("They were not in the table")

        # Add the person to the model
        model['users'][person.username] = {}
        model['users'][person.username]['totaly'] = 0

        # Update the totals in the table for words and the new user (totalx, totaly)
        update_table_totals(person)
    # If the user is not in the model...
    else:
        # print("They were in the table")

        # If the user does not have the exact same data as before...
        if set(person.words.keys()) != set(model['users'][person.username]['words'].keys()) or set(
                person.words.values()) != set(model['users'][person.username]['words'].values()):
            # print("They had different values from the ones in the table")

            # Subtract their previous values...
            for word in model['users'][person.username]['words']:
                model['words'][word]['totalx'] -= model['users'][person.username]['words'][word]
                model['totalxy'] -= model['users'][person.username]['words'][word]

            # And add their new values
            update_table_totals(person)


def update_table_totals(person):
    # Reset the user's data to 0 and their words to their frequency count
    model['users'][person.username]['words'] = person.words
    model['users'][person.username]['totaly'] = 0

    # Update the totals for each word the user has
    for word in person.words:
        model['users'][person.username]['totaly'] += person.words[word]
        if word not in model['words']:
            model['words'][word] = {}
        if 'totalx' not in model['words'][word]:
            model['words'][word]['totalx'] = person.words[word]
        else:
            model['words'][word]['totalx'] += person.words[word]


def calculate_user(person):
    # If the person is in the model
    if person.username in model['users']:

        # Set up needed variables
        interests = {}

        # For each word, calculate its Chi-Squared Contribution
        for word in person.words:
            score = float(model['users'][person.username]['words'][word]) / float(model['words'][word]['totalx'])
            interests[word] = score

        # Add the interests to the user object and print the interests
        person.add_interests(interests)
        # person.print_interests()
        save_model()


def save_model():
    with open('data/bayesModel.json', 'w') as file:
        json.dump(model, file)


def open_model():
    if not os.path.exists('data/bayesModel.json'):
        data = create_data()
    else:
        with open('data/bayesModel.json', 'r') as file:
            data = json.load(file)
    return data


def retrain_model():
    with open('data/handles.OLD.json', 'r') as path:
        people = list(json.load(path))
    for person in people:
        user = BayesUser(person)
        user.load_user_data()
        user.find_words()
        add_user(user)
    compute_table_total()


if __name__ == "__main__":
    open_model()
    model = create_data()
    compute_table_total()
    save_model()
else:
    model = open_model()
    compute_table_total()
