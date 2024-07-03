import json
import os
import re
import subprocess
import time
import urllib.request

from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher


def main():
    # files that will be used
    # files[0]: nix-unfiltered -> nix packages without any filtering
    # files[1]: nix -> nix packages after filtering
    # files[2]: flathub -> flathub packages
    files = ["./packages/nix-unfiltered", "./packages/nix", "./packages/flathub"]

    # check if dir exists, if not create it
    if not os.path.exists("./packages"):
        os.makedirs("./packages")

    get_nix_packages(files[0])
    filter_nix_packages(files[0], files[1])
    get_flathub_packages(files[2])
    check_similarity(files[1], files[2])


def get_nix_packages(f):
    if not os.path.exists(f):
        print("pull nix packages (can take up to a minute)")

        # get all nix packages
        s = subprocess.run(
            ["nix-env", "-qa"], capture_output=True, text=True
        ).stdout.lower()

        # write nix packages to file
        with open(f, "w") as file:
            file.write(s)

    else:
        # count packages
        with open(f, "r") as file:
            c = sum(1 for line in file)
        print("nix packages already exist (" + str(c) + " packages)")


def filter_nix_packages(fi, fo):
    print("filter nix packages")

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

    # remove "-git" if present in word
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

    # sort words alphabetically
    w.sort()

    # write words to file
    with open(fo, "w") as file:
        for word in w:
            file.write(word.lower())


def get_flathub_packages(f):
    if not os.path.exists(f):
        print("pull flathub packages (can take a few minutes)")

        a = []  # apps
        u = []  # urls
        n = []  # names
        v = []  # versions

        # get all app urls
        t = "https://flathub.org/api/v2/appstream"
        with urllib.request.urlopen(t) as x:
            x = json.load(x)
        u = [t + "/" + item for item in x]

        # get all app names and version
        with ThreadPoolExecutor(max_workers=10) as p:
            n = list(p.map(get_name, u))
            v = list(p.map(get_version, u))

        # set app name and app version into same format as nix packages (name-version)
        a = [
            n[i].replace(" ", "-") + "-" + v[i].replace(" ", "-") for i in range(len(x))
        ]

        # sort apps alphabetically
        a.sort()

        # write apps to file
        with open(f, "w") as file:
            file.writelines(line.lower() + "\n" for line in a)

    else:
        # count packages
        with open(f, "r") as file:
            c = sum(1 for line in file)
        print("flathub packages already exist (" + str(c) + " packages)")


def get_name(u):
    try:
        with urllib.request.urlopen(u) as x:
            a = json.load(x)
        time.sleep(0.75)
        return a["name"]
    except:
        print("error: " + u)
        return "error:" + u


def get_version(u):
    try:
        with urllib.request.urlopen(u) as x:
            a = json.load(x)
        time.sleep(0.75)
        return a["releases"][0]["version"]
    except:
        print("error: " + u)
        return "error:" + u


def check_similarity(f1, f2):
    print("find similar packages (can take a few minutes) (spam ctrl+c to cancel)")
    print("status / flathub / nix")

    n = []  # nix packages
    f = []  # flathub packages

    # get all packages from files
    with open(f1, "r") as file1, open(f2, "r") as file2:
        n = [line.rstrip() for line in file1]
        f = [line.rstrip() for line in file2]

    # remove last char
    n = [word[:-1] for word in n]
    f = [word[:-1] for word in f]

    # check similarity
    with ThreadPoolExecutor(max_workers=25) as p:
        for i in range(len(f)):
            p.submit(
                get_similarity, f[i], [word for word in n if word.startswith(f[i][0])]
            )


def get_similarity(a, b):
    for i in range(len(b)):
        x = SequenceMatcher(None, a, b[i]).ratio()
        # if apps have same name
        if x >= 0.825:
            # if apps have same version
            if x == 1:
                print("true / {} / {}".format(a, b[i]))
            else:
                print("false / {} / {}".format(a, b[i]))


main()
