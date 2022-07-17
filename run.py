import os
import shutil
from datetime import datetime
import argparse
import tweepy
import json
from render_preview import render_equation

BODY_MAP = {
    "conjecture": "Can you prove today's conjecture?",
    "proven": "Check out following proven conjecture we found today!",
    "unknown-lhs": "Today we received a PCF that we think might be some constant. Can you figure out which it is?",
}

parser = argparse.ArgumentParser()
parser.add_argument("file", nargs="?")
parser.add_argument("--dont-tweet", action=argparse.BooleanOptionalAction)
args = parser.parse_args()

filename = args.file
if not filename:
    queue_files = sorted(os.listdir("queue"))
    if len(queue_files) == 0:
        print("No tweets available in queue!")
        exit(-1)
    top = queue_files[0]
    filename = os.path.join("queue", top)

tweet_info = None
with open(filename, "r") as tweet_file:
    tweet_info = json.load(tweet_file)

body = BODY_MAP[tweet_info["type"]]
render_equation(tweet_info["equation"], transparent=False, max_aspect_ratio=16 / 9)

if not args.dont_tweet:
    # TODO: Move these to repository secrets
    auth = tweepy.OAuth1UserHandler(
        "",
        "",
        "",
        "",
    )

    api = tweepy.API(auth)
    api.update_status_with_media(body, "preview.png")

    today = datetime.now().strftime("%d_%m_%y")
    shutil.move(filename, f"posted/{today}.json")
