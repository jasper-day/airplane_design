"""
Code for calculating structural properties of wings and sections

Usage: `python structures.py` will output an example graph
"""

import math
import numpy as np
from scipy import integrate
from data import get_materials_like
import matplotlib.pyplot as plt

CFRP = get_materials_like('cfrp')[0] # youngs modulus in GPa
GFRP = get_materials_like('gfrp')[0] # youngs modulus in GPa
gravity = 9.81

def find_weight(mass, num_gs):
    """ Find the effective weight of a mass accelerating at `num_gs` times the acceleration due to gravity"""
    return mass * num_gs * gravity


def find_I_hollow_cyl(outer_diam, inner_diam):
    return math.pi/64 * (outer_diam**4 - inner_diam**4)

def find_J_hollow_cyl(outer_diam, inner_diam):
    return math.pi/32 * (outer_diam**4 - inner_diam**4)

def get_elliptic_lift_fn(ymin, ymax, lift_tot):
    """ Given ymin, ymax, and total lift, returns a function of y 
    corresponding to an elliptic lift distribution over y. """
    b = ymax - ymin # wingspan
    y0 = (ymax + ymin)/2
    ellipse = lambda y: np.sqrt(1 - (2*y)**2) # from -1/2 to 1/2
    # find lift at midpoint (0.785 = area under ellipse(y) )
    lift_0 = lift_tot/(b * 0.785398163397448)
    scaled_ellipse = lambda y: lift_0 * ellipse((y-y0)/b)
    return scaled_ellipse

def find_loading(W, y):
    """ Given a centered array of y-values, returns the loading distribution over the wing """
    # model elliptic lift over the wing
    lift = get_elliptic_lift_fn(min(y),max(y),W)
    loading = lift(y)
    # model airplane weight as a delta function at y=0
    loading[len(y)//2] -= np.sum(loading)
    return loading

def find_shear(loading, y):
    """ Finds shear given loading conditions """
    shear = integrate.cumulative_trapezoid(loading, y)
    # free end boundary condition
    shear -= shear[0]
    return shear

def find_moment(shear, y):
    """ Finds moment acting on the wing given shear """
    moment = integrate.cumulative_trapezoid(shear, y)
    # free end boundary condition
    moment -= moment[0]
    return moment

def find_angle(moment, y, youngs_mod, I_zz):
    """ Finds the y-relative angle of the wing given moment """
    # angle of beam at given moment
    theta = integrate.cumulative_trapezoid(moment, y) / (I_zz * youngs_mod)
    # fixed center boundary condition
    theta -= theta[len(y)//2]
    return theta

def find_displacement(theta, y):
    """ Finds the vertical displacement of the wing given angle """
    # vertical displacement
    disp = integrate.cumulative_trapezoid(theta, y)
    # fixed center boundary condition
    disp -= disp[len(y)//2]
    return disp

def plot_data(ax, y, data, color="black", xlabel="", ylabel=""):
    ax.plot(y, data, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def make_all_charts(axs, y, loading, youngs_mod, I_zz):
    shear = find_shear(loading, y)
    moment = find_moment(shear, y[:-1])
    angle = find_angle(moment, y[:-2], youngs_mod, I_zz)
    disp = find_displacement(angle, y[:-3])
    plot_data(axs[0,0], y[:-1], shear, ylabel="shear (N)")
    plot_data(axs[1,0], y[:-2], moment, ylabel="moment (N.m)")
    plot_data(axs[0,1], y[:-3], angle, ylabel="angle (rad)")
    plot_data(axs[1,1], y[:-4], disp, ylabel="displacement (m)")
    # axs[0,0].axis([min(y)-0.5, max(y)+0.5, -1, max(loading)])

def get_parameters(material, outer_diam, inner_diam, b, W, gs):
    if material in ['cfrp', 'CFRP']:
        youngs_mod = (CFRP.E_lower + CFRP.E_upper)/2 * 1e9
    elif material in ['gfrp', 'GFRP']:
        youngs_mod = (GFRP.E_lower + GFRP.E_upper)/2 * 1e9
    else:
        raise ValueError(f"material {material} not recognized")
    weight = find_weight(W, gs)
    I_zz = find_I_hollow_cyl(outer_diam, inner_diam)
    y = np.linspace(-b/2, b/2, 1000)
    loading = find_loading(weight, y)
    return {"y":y, "loading":loading, "youngs_mod":youngs_mod, "I_zz":I_zz}

if __name__ == "__main__":
    youngs_mod_cfrp = (CFRP.E_lower + CFRP.E_upper)/2 * 1e9
    I_zz = find_I_hollow_cyl(0.025,0.020) # 25mm OD by 20mm ID
    y = np.linspace(-1.2, 1.2, 1000)
    loading = find_loading(find_weight(3,6), y)
    fig,axs = plt.subplots(2,2)
    make_all_charts(axs, y, loading, youngs_mod_cfrp, I_zz)
    plt.show()
