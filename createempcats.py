from empath import Empath
import sys
import json
from cnrelated import get_related_terms
from os import path

emp = Empath()

# If -d specified delete the categories to start fresh
if len(sys.argv) > 2:
    if sys.argv[2] == "-d":
        with open(sys.argv[1], "r") as file:
            obj = json.load(file)
        for word in obj["topics"]:
            print(word)
            emp.delete_category(word)
# Otherwise, load up the topics and create categories from them
elif len(sys.argv) == 2:
    with open(sys.argv[1], "r") as file:
        obj = json.load(file)
    for word in obj["topics"]:
        # Check to see if a category already exists to ensure we aren't overwriting them every time
        if not path.exists("venv/Lib/site-packages/empath/data/user/"+word+".empath"):
            # Get the related words from ConceptNet to use as a seed for creating the category
            seeds = get_related_terms(word)
            print(word, seeds)
            # Create the category for word
            emp.create_category(word, seeds)
