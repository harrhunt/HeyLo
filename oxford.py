# for more information on how to install requests# http://docs.python-requests.org/en/master/user/install/#install
import glob
import re
import time

import requests
import json
from os.path import exists
from credentials import OXFORD_APP_KEY, OXFORD_APP_ID


def get_entries(word):
    path = f"data/words/{word.lower()}.json"
    with open("404.json", "r") as file:
        missing = json.load(file)
    if word in missing:
        return 4041
    if exists(path):
        # print("Loaded from file")
        with open(path, "r") as file:
            data = json.load(file)
    else:
        url = f'https://od-api.oxforddictionaries.com/api/v2/entries/en-us/{word.lower()}?strictMatch=true'
        r = requests.get(url, headers={'app_id': OXFORD_APP_ID, 'app_key': OXFORD_APP_KEY})
        if r.status_code == 200:
            data = r.json()
            with open(path, "w") as file:
                json.dump(data, file)
        elif r.status_code == 404:
            missing.append(word)
            with open("404.json", "w") as file:
                json.dump(missing, file)
            return r.status_code
        else:
            return r.status_code
    return data["results"]


def get_lemmas(word):
    path = f"data/lemmas/{word.lower()}.json"
    with open("404.json", "r") as file:
        missing = json.load(file)
    if word in missing:
        return 4041
    if exists(path):
        # print("Loaded from file")
        with open(path, "r") as file:
            data = json.load(file)
    else:
        url = f'https://od-api.oxforddictionaries.com/api/v2/lemmas/en/{word.lower()}'
        r = requests.get(url, headers={'app_id': OXFORD_APP_ID, 'app_key': OXFORD_APP_KEY})
        if r.status_code == 200:
            data = r.json()
            with open(path, "w") as file:
                json.dump(data, file)
        elif r.status_code == 404:
            missing.append(word)
            with open("404.json", "w") as file:
                json.dump(missing, file)
            return r.status_code
        else:
            return r.status_code
    return data["results"]


def get_defs(word, combine_lexical=True, sub_definitions=False):
    definitions = []
    combined_definitions = []
    results = get_entries(word)
    if isinstance(results, int):
        return "404: word not found"
    if combine_lexical:
        for result in results:
            # print(f"RESULT: {result}\n")
            for lex in result["lexicalEntries"]:
                # print(f"LEXICAL_ENTRY: {lex}\n")
                for entry in lex["entries"]:
                    # print(f"ENTRY: {entry}\n")
                    for sense in entry["senses"]:
                        # print(f"SENSE: {sense}\n")
                        if "definitions" in sense:
                            for definition in sense["definitions"]:
                                # print(f"DEFINITION: {definition}\n")
                                combined_definitions.append(definition)
            definitions.append(" & ".join(combined_definitions))
            combined_definitions = []
    else:
        for result in results:
            for lex in result["lexicalEntries"]:
                for entry in lex["entries"]:
                    for sense in entry["senses"]:
                        if "definitions" in sense:
                            for definition in sense["definitions"]:
                                definitions.append(definition)
                        if sub_definitions:
                            if "subsenses" in sense:
                                for subsense in sense["subsenses"]:
                                    for subdefinition in subsense["definitions"]:
                                        definitions.append(subdefinition)

    return definitions


def get_all_coarse_defs(word):
    words = get_lemma_words(word)
    if words is None:
        return None
    definitions = []
    for word in words:
        definitions.extend(get_defs(word))
    return definitions


def get_lemma_words(word):
    words = []
    results = get_lemmas(word)
    if isinstance(results, int):
        print(results)
        return None
    for result in results:
        for lex in result["lexicalEntries"]:
            for inflection in lex["inflectionOf"]:
                words.append(inflection["id"])
    return words


def save_words_not_found(wnf):
    with open("404.json", "w") as file:
        json.dump(wnf, file)


def gather_for_relations():
    global name, words
    with open("404.json", "r") as file:
        words_not_found = json.load(file)
    files = glob.glob("data/comparisons/*.json")
    for filename in files:
        name = re.split("[/\\\\]", filename)[-1]
        name = name.split(".")[0]
        words = name.split("-")
        for word in words:
            if exists(f"data/words/{word}.json"):
                continue
            elif word in words_not_found:
                continue
            print(word)
            results = get_entries(word)
            if isinstance(results, int) and results != 200:
                print(results)
                if results != 404:
                    save_words_not_found(words_not_found)
                    exit(1)
                words_not_found.append(word)
            time.sleep(1)
    save_words_not_found(words_not_found)


if __name__ == '__main__':
    # gather_for_relations()
    print(get_defs("bat"))
