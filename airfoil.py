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
    "bambino": r"bambino\d?",
    "lockheed": r"c(\d\w)?(\d{3}\w)?",
    "clark": r"clar[ky]\w+",
    "coanda": r"coanda\d",
    "curtiss": r"c(r\w+)?(urtis\w+)",
    "dae": r"dae\d{2}",
    "davis": r"davis[a-z_]*",
    
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

