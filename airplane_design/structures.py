"""
Code for calculating structural properties of wings and sections
"""

import math
import numpy as np
from scipy import integrate

def find_I_hollow_cyl(outer_diam, inner_diam):
    return math.pi/64 * (outer_diam**4 - inner_diam**4)

def find_J_hollow_cyl(outer_diam, inner_diam):
    return math.pi/32 * (outer_diam**4 - inner_diam**4)

def elliptic_lift_distribution(y, L_tot):
    b = max(y) - min(y)

