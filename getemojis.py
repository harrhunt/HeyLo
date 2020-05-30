import json
import operator
import os
import re
from csv import reader

import requests
import glob
import sys


def get_emojis():
    with open("data/emojis/emoji_df.csv", mode="r", encoding="utf-8", newline="") as file:
        lines = reader(file)
        emojis = []
        for emoji in lines:
            if ":" not in emoji[1] and "," not in emoji[1]:
                clean = re.sub(r"[^a-zA-Z0-9\s-]+", "", emoji[1])
                lowered = clean.lower()
                emoji = lowered.split()
                emoji = '-'.join(emoji)
                emojis.append(emoji)
    for emoji in emojis:
        if not os.path.exists(f"data/emojis/{emoji}.svg"):
            print(emoji)
            save_emoji(emoji)
            if not os.path.exists(f"data/emojis/{emoji}.png"):
                convert_to_png(emoji)
        elif not os.path.exists(f"data/emojis/{emoji}.png"):
            convert_to_png(emoji)


def save_emoji(emoji):
    directory = os.path.dirname(f"data/emojis/")
    try:
        os.makedirs(directory)
    except IOError as err:
        err = None

    svg = requests.get(f"https://api.iconify.design/twemoji:{emoji}.svg").text
    with open(f"data/emojis/{emoji}.svg", "w") as pic:
        pic.write(svg)


def clean_old_emojis():
    files = glob.glob(f"data/emojis/*.svg")
    for file in files:
        os.remove(file)

    files = glob.glob(f"data/emojis/*.png")
    for file in files:
        os.remove(file)


def convert_to_png(emoji):
    os.system(f'inkscape -z -e data/emojis/{emoji}.png -w 1024 -h 1024 data/emojis/{emoji}.svg')
