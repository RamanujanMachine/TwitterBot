import os
import shutil
from datetime import datetime
import argparse
import tweepy
import json
from render_preview import render_preview

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    parser.add_argument("--dont-tweet", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    filename = args.file
    if not filename:
        queue_files = sorted(os.listdir("queue"))
        queue_files.remove(".gitkeep")
        if len(queue_files) == 0:
            print("No tweets available in queue!")
            exit(-1)
        top = queue_files[0]
        filename = os.path.join("queue", top)

    tweet_info = None
    with open(filename, "r") as tweet_file:
        tweet_info = json.load(tweet_file)

    body = tweet_info["body"]
    with open("tmp.tex", "w") as tmp_tex_file:
        tmp_tex_file.write(tweet_info["tex"])
    render_preview("tmp.tex", transparent=False, max_aspect_ratio=16 / 9)

    if not args.dont_tweet:
        auth = tweepy.OAuth1UserHandler(
            os.environ["CONSUMER_TOKEN"],
            os.environ["CONSUMER_SECRET"],
            os.environ["ACCESS_TOKEN"],
            os.environ["ACCESS_TOKEN_SECRET"],
        )

        api = tweepy.API(auth)
        api.update_status_with_media(body, "preview.png")

        today = datetime.now().strftime("%d_%m_%y")
        shutil.move(filename, f"posted/{today}.json")
