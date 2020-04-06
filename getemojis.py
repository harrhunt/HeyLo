import json
import operator
import os
import requests
import glob
import sys


def get_emojis(emojis):
    if type(emojis) is not list:
        emojis = list(emojis)
    for emoji in emojis:
        if not os.path.exists(f"data/emojis/{emoji}.svg"):
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
