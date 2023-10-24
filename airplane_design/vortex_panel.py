"""
First-order numerical panel solver.
"""

import re
import matplotlib.pyplot as plt
import numpy as np
import os

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
        airfoil = parse_coordinates(lines)
    except ValueError as e:
        e.add_note(f"At file: {filename}")
        raise e
    if airfoil:
        fdata = os.path.split(filename)
        path = fdata[0]
        fname = fdata[1]
        airfoil["filename"] = fname
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
    return res

filename_regexes = {
    "ag (mark drela)": r"ag\d{2}(.*)?",
    "althaus": r"ah\d\d(.*)?",
    "nasa ames": r"ames\d\d",
    "amsoil": r"amsoil\d",
    "arad:": r"arad\d{2}",
    "ananda-selig": r"as\d{4}",
    "boeing": r"b(7\d\d.)?(oe\d{3})?(ac.*)?",
    "bambino": r"e?bambino\d?",
    "lockheed": r"c(\d\w)?(\d{3}\w)?",
    "clark": r"clar[ky]\w+",
    "coanda": r"coanda\d",
    "curtiss": r"c(r\w+)?(urtis\w+)",
    "dae": r"dae\d{2}",
    "davis": r"davis[a-z_]*",
    "daytona-wright": r"dayton\w*",
    "sikorsky": r"(dbln\d{3})?(gs\d)?|sc\d{4}(\D.*)?|ssca\d+",
    "defiant": r"def\w+",
    "e-series": r"e\d+",
    "eh-series": r"eh\d{4}",
    "eiffel (wright)": r"eiffel\d+",
    "fage & collins": r"fg\d",
    "wortmann fx": r"fx\w+",
    "giii": r"giii\w",
    "glenn martin": r"(glenn\w+)?(gm\w+)",
    "goe (gottingen)": r"goe\w+",
    "hq": r"hq\d+\w+",
    "ham-std": r"hs\d+",
    "ht": r"ht\d\d",
    "isa": r"isa\d+",
    "ist": r"ist[a-z0-9-]+",
    "nasa low-speed": r"ls\d+(mod)?",
    "naca-m": r"(naca)?m\d\d?",
    "marske": r"marske\d",
    "mh": r"mh\d+",
    "nasa ms": r"ms\d+",
    "naca h-series": r"n\dh\d+",
    "nasa/naca": r"n.*",
    "naca 4-digit": r"n(aca)?\d{4}\D+",
    "naca 5-digit": r"n\d{5}\D+|naca\d{2}[a-z0-9-]\d{3}|naca\d{5}",
    "naca 6-digit": r"naca\d{3}\D\d{3}|naca\d{6}",
    "nasa nlf": r"nlf.+",
    "nasa rc": r"rc.*",
    "nasa sc": r"sc\d{5}",
    "p-51d": r"p51.*",
    "rae": r"rae\d+.*",
    "raf": r"raf\d+.*",
    "rg": r"rg.*",
    "rhodes": r"rhodes.*",
    "s-4digit human powered": r"s\d{4}.*",
    "sd-4digit": r"sd\d{4}",
    "sg-4digit": r"sg\d{4}",
    "usa": r"usa\w+",
    "boeing vtol": r"v\d{5}|vr.*",
}


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

