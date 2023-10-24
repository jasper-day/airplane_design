"""
Import and parse airfoil data
"""

import re
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def parse_dir(directory):
    files = os.listdir(directory)
    airfoils = []
    for file in files:
        airfoil = parse_file(os.path.join(directory, file))
        airfoils.append(airfoil)
    return airfoils


def parse_file(filename):
    """ Parses an airfoil data file into a list of coordinates """
    if os.path.splitext(filename)[1] != '.dat':
        raise FileNotFoundError(f"Bad extension: {os.path.splitext(filename)}")
    try:
        with open(filename) as file:
            lines = file.readlines()
    except Exception as e:
        e.add_note(f"Error opening file: {filename}")
        raise e
    try:
        airfoil = _parse_coordinates(lines)
    except ValueError as e:
        e.add_note(f"At file: {filename}")
        raise e
    if airfoil:
        fdata = os.path.split(filename)
        path = fdata[0]
        fname_data = os.path.splitext(fdata[1])
        filename = fname_data[0]
        extension = fname_data[1]
        airfoil["filename"] = filename
        airfoil["extension"] = extension
        airfoil["path"] = path
        return airfoil
    else:
        return None

def _parse_coordinates(lines):
    # Strip whitespace
    lines = [line.strip() for line in lines if line.strip()]
    # First line is the title
    title = lines[0]
    coords = []
    number_regex = re.compile(r"[0-9.-]+")
    for line in lines[1:]:
        # Find x and y coordinates
        numbers = number_regex.findall(line)
        if len(numbers) != 2:
            raise ValueError(f"Could not parse line (regex did not match): {line}")
        x = float(numbers[0])
        y = float(numbers[1])
        coords.append((x, y))
    res = {"title": title, "coordinates": coords}
    # find upper and lower planforms

    return res

filename_regexes = {
    "ag (mark drela)":re.compile(r"ag\d{2}(.*)?"),
    "althaus":        re.compile(r"ah\d\d(.*)?"),
    "nasa ames":      re.compile(r"ames\d\d"),
    "amsoil":         re.compile(r"amsoil\d"),
    "arad: ":         re.compile(r"arad\d{2}"),
    "ananda-selig":   re.compile(r"as\d{4}"),
    "boeing":         re.compile(r"b(7\d\d.)?(oe\d{3})?(ac.*)?"),
    "bambino":        re.compile(r"e?bambino\d?"),
    "lockheed":       re.compile(r"c(\d\w)?(\d{3}\w)?"),
    "clark":          re.compile(r"clar[ky]\w+"),
    "coanda":         re.compile(r"coanda\d"),
    "curtiss":        re.compile(r"c(r\w+)?(urtis\w+)"),
    "dae":            re.compile(r"dae\d{2}"),
    "davis":          re.compile(r"davis[a-z_]*"),
    "daytona-wright": re.compile(r"dayton\w*"),
    "sikorsky":       re.compile(r"(dbln\d{3})?(gs\d)?|sc\d{4}(\D.*)?|ssca\d+"),
    "defiant":        re.compile(r"def\w+"),
    "e-series":       re.compile(r"e\d+"),
    "eh-series":      re.compile(r"eh\d{4}"),
    "wright eiffel":  re.compile(r"eiffel\d+"),
    "fage & collins": re.compile(r"fg\d"),
    "wortmann fx":    re.compile(r"fx\w+"),
    "giii":           re.compile(r"giii\w"),
    "glenn martin":   re.compile(r"(glenn\w+)?(gm\w+)"),
    "goe gottingen":  re.compile(r"goe\w+"),
    "hq":             re.compile(r"hq\d+\w+"),
    "ham-std":        re.compile(r"hs\d+"),
    "ht":             re.compile(r"ht\d\d"),
    "isa":            re.compile(r"isa\d+"),
    "ist":            re.compile(r"ist[a-z0-9-]+"),
    "nasa low-speed": re.compile(r"ls\d+(mod)?"),
    "naca-m":         re.compile(r"(naca)?m\d\d?"),
    "marske":         re.compile(r"marske\d"),
    "mh":             re.compile(r"mh\d+"),
    "nasa ms":        re.compile(r"ms\d+"),
    "naca h-series":  re.compile(r"n\dh\d+"),
    "nasa/naca":      re.compile(r"n.*"),
    "naca 4-digit":   re.compile(r"n(aca)?\d{4}\D+"),
    "naca 5-digit":   re.compile(r"n[012345789]\d{4}\D+|naca[012345789]\d[a-z0-9-]\d{3}|naca[012345789]\d{4}"),
    "naca 6-series":  re.compile(r"n6\d{4}\D+|naca6\d{1}[a-z0-9-]\d{3}|naca6\d{4}"),
    "naca 6-digit":   re.compile(r"naca\d{3}\D\d{3}|naca\d{6}"),
    "nasa nlf":       re.compile(r"nlf.+"),
    "nasa rc":        re.compile(r"rc.*"),
    "nasa sc":        re.compile(r"sc\d{5}"),
    "p-51d":          re.compile(r"p51.*"),
    "rae":            re.compile(r"rae\d+.*"),
    "raf":            re.compile(r"raf\d+.*"),
    "rg":             re.compile(r"rg.*"),
    "rhodes":         re.compile(r"rhodes.*"),
    "s-4digit hpv":   re.compile(r"s\d{4}.*"),
    "sd-4digit":      re.compile(r"sd\d{4}"),
    "sg-4digit":      re.compile(r"sg\d{4}"),
    "usa":            re.compile(r"usa\w+"),
    "boeing vtol":    re.compile(r"v\d{5}|vr.*"),
}

def find_re(name):
    return filename_regexes[name]

def regex_pred(regex):
    return lambda airfoil: regex.fullmatch(airfoil["filename"])

def no_regex_pred(regex_dict):
    def predicate(airfoil):
        res = True
        for regex in regex_dict.values():
            if regex.fullmatch(airfoil["filename"]):
                res = False
                break
        return res
    return predicate

def matching_foils(regex, airfoils):
    return [foil for foil in filter(regex_pred(regex), airfoils)]

def plot_coordinates(ax, coordinates, title=None, plot_chord=False):
    coords = np.array(coordinates)
    ax.plot(coords[:,0], coords[:,1], color="black", label=title)
    if plot_chord:
        ax.plot([1,0], [0,0], color="red", linestyle='--')
    ax.set_aspect("equal")
    # ax.legend()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel(title[:30])

def make_subplots(axs, airfoils, nrows, ncols):
    for i in range(nrows):
        for j in range(ncols):
            airfoil = airfoils[j + ncols*i]
            plot_coordinates(axs[i,j], airfoil["coordinates"], airfoil["title"])


def main(argv = []):
    if argv:
        path = argv[1]
        if os.path.exists(path):
            if os.path.isdir(path):
                try:
                    airfoils = parse_dir(path)
                except Exception as e:
                    print(e)
            elif os.path.isfile(path):
                try:
                    airfoil = parse_file(path)
                except Exception as e:
                    print(e)
            else:
                print(f"Could not find directory or file: {path}")
    else:
        print("Please run with a file name or directory.")

if __name__ == "__main__":
    main(sys.argv)
