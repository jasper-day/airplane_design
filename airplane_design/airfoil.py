"""
Import and parse airfoil data

airfoil:
{
    "title": Name of the airfoil
    "filename": filename (no extension)
    "extension": file extension
    "path": path to .dat file
    "coordinates": list of [x,y] tuples defining the airfoil
    "upper_planform": list of [x,y] tuples defining the top surface of the airfoil
    "lower_planform": list of [x,y] tuples defining the lower surface of the airfoil
    "thickness": thickness of airfoil as a multiple of chord
}
"""

import re
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from scipy import interpolate
from data import Airfoil

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
        airfoil_dict = _parse_coordinates(lines)
    except ValueError as e:
        e.add_note(f"At file: {filename}")
        raise e
    if airfoil_dict:
        fdata = os.path.split(filename)
        path = fdata[0]
        fname_data = os.path.splitext(fdata[1])
        filename = fname_data[0]
        extension = fname_data[1]
        airfoil_dict["filename"] = filename
        airfoil_dict["extension"] = extension
        airfoil_dict["path"] = path
        # ORM class
        airfoil = Airfoil(**airfoil_dict)
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
        coords.append([x, y])
    res = {"title": title, "coordinates": coords}
    # find upper and lower planforms
    if [0,0] not in coords:
        origin_index = find_sign_change(coords)
    else:
        origin_index = coords.index([0,0])
    upper_planform = coords[:origin_index+1]
    # Make sure trailing edge is included
    if [1,0] not in upper_planform:
        upper_planform.insert(0, (1,0))
    lower_planform = coords[origin_index:]
    if [1,0] not in lower_planform:
        lower_planform.append([1,0])
    res["upper_planform"] = upper_planform
    res["lower_planform"] = lower_planform
    # Find airfoil thickness
    thickness = find_thickness(upper_planform, lower_planform)
    res["thickness"] = thickness
    return res

def find_sign_change(coordinates):
    for i in range(len(coordinates) - 2):
        y1 = coordinates[i][0]
        y2 = coordinates[i + 1][0]
        y3 = coordinates[i + 2][0]
        d1 = y2 - y1
        d2 = y3 - y2
        if np.sign(d1) == -1 and np.sign(d2) != np.sign(d1):
            return i
    raise ValueError("Sign change not found")

def find_thickness(upper,lower):
    get_ys = lambda coords: [y for [x,y] in coords]
    get_xs = lambda coords: [x for [x,y] in coords]
    # linear interpolation between values
    f_upper = interpolate.interp1d(get_xs(upper), get_ys(upper))
    f_lower = interpolate.interp1d(get_xs(lower), get_ys(lower))
    f_thickness = lambda x: f_upper(x) - f_lower(x)
    x = np.linspace(0,1,1000)
    y = f_thickness(x)
    return max(y)


filename_regexes = {
    "ag (mark drela)":r"ag\d{2}(.*)?",
    "althaus":        r"ah\d\d(.*)?",
    "nasa ames":      r"ames\d\d",
    "amsoil":         r"amsoil\d",
    "arad: ":         r"arad\d{2}",
    "ananda-selig":   r"as\d{4}",
    "boeing":         r"b(7\d\d.)?(oe\d{3})?(ac.*)?",
    "bambino":        r"e?bambino\d?",
    "lockheed":       r"c(\d\w)?(\d{3}\w)?",
    "clark":          r"clar[ky]\w+",
    "coanda":         r"coanda\d",
    "curtiss":        r"c(r\w+)?(urtis\w+)",
    "dae":            r"dae\d{2}",
    "davis":          r"davis[a-z_]*",
    "daytona-wright": r"dayton\w*",
    "sikorsky":       r"(dbln\d{3})?(gs\d)?|sc\d{4}(\D.*)?|ssca\d+",
    "defiant":        r"def\w+",
    "e-series":       r"e\d+",
    "eh-series":      r"eh\d{4}",
    "wright eiffel":  r"eiffel\d+",
    "fage & collins": r"fg\d",
    "wortmann fx":    r"fx\w+",
    "giii":           r"giii\w",
    "glenn martin":   r"(glenn\w+)?(gm\w+)",
    "goe gottingen":  r"goe\w+",
    "hq":             r"hq\d+\w+",
    "ham-std":        r"hs\d+",
    "ht":             r"ht\d\d",
    "isa":            r"isa\d+",
    "ist":            r"ist[a-z0-9-]+",
    "nasa low-speed": r"ls\d+(mod)?",
    "naca-m":         r"(naca)?m\d\d?",
    "marske":         r"marske\d",
    "mh":             r"mh\d+",
    "nasa ms":        r"ms\d+",
    "naca h-series":  r"n\dh\d+",
    "nasa/naca":      r"n.*",
    "naca 4-digit":   r"n(aca)?\d{4}\D+",
    "naca 5-digit":   r"n[012345789]\d{4}\D+|naca[012345789]\d[a-z0-9-]\d{3}|naca[012345789]\d{4}",
    "naca 6-series":  r"n6\d{4}\D+|naca6\d{1}[a-z0-9-]\d{3}|naca6\d{4}",
    "naca 6-digit":   r"naca\d{3}\D\d{3}|naca\d{6}",
    "nasa nlf":       r"nlf.+",
    "nasa rc":        r"rc.*",
    "nasa sc":        r"sc\d{5}",
    "p-51d":          r"p51.*",
    "rae":            r"rae\d+.*",
    "raf":            r"raf\d+.*",
    "rg":             r"rg.*",
    "rhodes":         r"rhodes.*",
    "s-4digit hpv":   r"s\d{4}.*",
    "sd-4digit":      r"sd\d{4}",
    "sg-4digit":      r"sg\d{4}",
    "usa":            r"usa\w+",
    "boeing vtol":    r"v\d{5}|vr.*",
}

#Functions no longer needed
#def find_re(name):
#    return re.compile(filename_regexes[name])
#
#def regex_pred_fn(regex):
#    return lambda airfoil: regex.fullmatch(airfoil["filename"])
#
#def no_regex_pred(regex_dict):
#    def predicate(airfoil):
#        res = True
#        for regex in regex_dict.values():
#            if regex.fullmatch(airfoil["filename"]):
#                res = False
#                break
#        return res
#    return predicate
#
#def matching_foils_fn(regex, airfoils):
#    return [foil for foil in filter(regex_pred(regex), airfoils)]
#
#def sort_by_name(airfoils):
#    airfoils.sort(key=lambda airfoil: airfoil['filename'])

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

def make_subplots(axs, coordinates, titles, nrows, ncols):
    for i in range(nrows):
        for j in range(ncols):
            coords = coordinates[j + ncols*i]
            title = titles[j + ncols*i]
            plot_coordinates(axs[i,j], coords, title)


def main(argv = []):
    from data import insert_airfoil, insert_airfoils
    if argv:
        path = argv[1]
        if os.path.exists(path):
            if os.path.isdir(path):
                try:
                    airfoils = parse_dir(path)
                    insert_airfoils(airfoils)
                except Exception as e:
                    print(e)
            elif os.path.isfile(path):
                try:
                    airfoil = parse_file(path)
                    insert_airfoil(airfoil)
                except Exception as e:
                    print(e)
            else:
                print(f"Could not find directory or file: {path}")
    else:
        print("Please run with a file name or directory.")

if __name__ == "__main__":
    main(sys.argv)
