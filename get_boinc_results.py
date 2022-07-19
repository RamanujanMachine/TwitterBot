from urllib.request import Request, urlopen


def get_webpage(address: str) -> str:
    response = urlopen(Request(address, headers={"User-Agent": "Mozilla/5.0"}))
    return response.read().decode()


def get_available_results():
    return map(
        lambda t: t[:-3],
        filter(
            lambda t: t.startswith("RNM"),
            get_webpage("https://rnma.xyz/boinc/result").split(">"),
        ),
    )


if __name__ == "__main__":
    import os

    downloaded = os.listdir("boinc_results")
    print("Getting available results")
    results_to_download = filter(lambda t: t not in downloaded, get_available_results())
    for result in results_to_download:
        print("Downloading: " + result)
        with open(os.path.join("boinc_results", result), "w") as result_file:
            result_file.write(get_webpage("https://rnma.xyz/boinc/result/" + result))
