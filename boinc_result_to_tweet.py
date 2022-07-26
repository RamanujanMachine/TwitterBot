from boinc_result_to_tex import generate_tex

BODY_MAP = {
    "conjecture": "Check out today's conjecture!",
    "unknown-lhs": "Check out following proven conjecture we found today!",
}


def generate_tweet(result_filename: str):
    tex, template = generate_tex(result_filename)
    return {"body": BODY_MAP[template], "tex": tex}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()
    print(json.dumps(generate_tweet(args.file)))
