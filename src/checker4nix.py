import json
import os
import subprocess
import time
import urllib.request

from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher


class colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PINK = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    ULINE = "\033[4m"
    END = "\033[0m"


def main():
    # files that will be used
    # files[0]: nix-unfiltered -> nix packages without any filtering
    # files[1]: nix -> nix packages after filtering
    # files[2]: flathub-unfiltered -> flathub packages without any filtering
    # files[3]: flathub -> flathub packages after filtering
    files = [
        "./packages/nix-unfiltered",
        "./packages/nix",
        "./packages/flathub-unfiltered",
        "./packages/flathub",
    ]

    # check if dir exists, if not create it
    if not os.path.exists("./packages"):
        os.makedirs("./packages")

    get_nix_packages(files[0])
    filter_packages(files[0], files[1], "nix")
    get_flathub_packages(files[2])
    filter_packages(files[2], files[3], "flathub")
    check_similarity(files[1], files[3])


def get_nix_packages(f):
    if not os.path.exists(f):
        print("pull nix packages (can take up to a minute)")

        # get all nix packages
        s = subprocess.run(
            ["nix-env", "-qa"], capture_output=True, text=True
        ).stdout.lower()

        # write to file
        with open(f, "w") as file:
            file.write(s)

    else:
        # count packages
        with open(f, "r") as file:
            c = sum(1 for line in file)
        print("nix packages already exist (" + str(c) + " packages)")


def filter_packages(fi, fo, str):
    print(f"filter {str} packages")

    w = []  # words
    wu = [  # unwanted chars / words
        "=",
        "+",
        "unstable",
        "test",
        "demo",
        "alpha",
        "beta",
        "pre",
        "dev",
        "snapshot",
        "staging",
        "old",
        "deprecated",
        "obsolete",
        "broken",
        "outdated",
        "legacy",
        "error",
    ]
    vn = {}  # newest versions

    # delete old file if it exists
    if os.path.exists(fo):
        os.remove(fo)

    # get all packages from file
    with open(fi, "r") as file:
        w = file.readlines()

    # filter out words that are in wu
    w = [word for word in w if not any(unwanted_word in word for unwanted_word in wu)]

    # remove "-git" item if present in word
    w = [word.replace("-git\n", "\n") for word in w]

    # remove duplicated words
    w = list(set(w))

    # only keep newest version
    for i in w:
        n, v = i.split("-")[:-1], i.split("-")[-1]
        n = tuple(n)
        if n in vn:
            if v > vn[n]:
                vn[n] = v
        else:
            vn[n] = v
    w = [f'{"-".join(n)}-{v}' for n, v in vn.items()]

    # sort alphabetically
    w.sort()

    # write to file
    with open(fo, "w") as file:
        for word in w:
            file.write(word.lower())


def get_flathub_packages(f):
    if not os.path.exists(f):
        print("pull flathub packages (can take a few minutes)")

        a = []  # apps
        u = []  # urls

        # get all app urls
        t = "https://flathub.org/api/v2/appstream"
        with urllib.request.urlopen(t) as x:
            x = json.load(x)
        u = [t + "/" + item for item in x]

        # get all app names and versions
        with ThreadPoolExecutor(max_workers=10) as p:
            a = list(p.map(get_name_and_version, u))

        # sort alphabetically
        a.sort()

        # write to file
        with open(f, "w") as file:
            file.writelines(line.lower() + "\n" for line in a)

    else:
        # count packages
        with open(f, "r") as file:
            c = sum(1 for line in file)
        print("flathub packages already exist (" + str(c) + " packages)")


def get_name_and_version(u):
    try:
        with urllib.request.urlopen(u) as x:
            a = json.load(x)
        time.sleep(0.5)
        result = a["name"] + "-" + a["releases"][0]["version"]
        result = result.replace(" ", "-")
        return result
    except:
        print("error: " + u)
        return "error:" + u


def check_similarity(f1, f2):
    print("find similar packages (can take a few minutes) (spam ctrl+c to cancel)")
    print("status / flathub / nix")

    n = []  # nix packages
    f = []  # flathub packages

    # read from files
    with open(f1, "r") as file1, open(f2, "r") as file2:
        n = [line.rstrip() for line in file1]
        f = [line.rstrip() for line in file2]

    # remove last char
    n = [word[:-1] for word in n]
    f = [word[:-1] for word in f]

    # stats
    total = len(f)  # total number of packages (flathub)
    matches = 0  # number of matches
    misses = 0  # number of misses
    true = 0  # number of true matches
    false = 0  # number of false matches

    # check similarity
    with ThreadPoolExecutor(max_workers=25) as p:
        for i in range(len(f)):
            r = p.submit(
                get_similarity, f[i], [word for word in n if word.startswith(f[i][0])]
            )
            # count stats
            if r.result() == "True-True" or r.result() == "True-False":
                matches += 1
                if r.result() == "True-True":
                    true += 1
                else:
                    false += 1
            else:
                misses += 1

    # print stats
    print(f"\nTotal: {total} (flathub packages)")
    print(f"Matches: {matches}")
    print(f"Misses: {misses}")
    true_percentage = (true / matches) * 100
    false_percentage = (false / matches) * 100
    print(f"True: {true} ({true_percentage:.2f}%)")
    print(f"False: {false} ({false_percentage:.2f}%)")


def get_similarity(a, b):
    # add tabs based on length for better formatting
    if len(a) < 14:
        t = "\t\t"
    else:
        t = "\t"

    found = "False"
    for i in range(len(b)):
        x = SequenceMatcher(None, a, b[i]).ratio()
        # if have same name
        if x >= 0.825:
            # if have same version
            if x == 1:
                print(f"{colors.GREEN}true{colors.END}\t/ {a}{t}/ {b[i]}")
                found = "True-True"
            else:
                print(f"{colors.RED}false{colors.END}\t/ {a}{t}/ {b[i]}")
                found = "True-False"
    if found == "False":
        print(f"{colors.YELLOW}missing{colors.END}\t/ {a}{t}/ -")

    return found


main()
