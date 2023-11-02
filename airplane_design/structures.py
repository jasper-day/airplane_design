"""
Code for calculating structural properties of wings and sections

Usage: `python structures.py` will output an example graph
"""

import math
import numpy as np
from scipy import integrate
from data import get_materials_like, Material
import matplotlib.pyplot as plt

mat_dict = {
    "cfrp (lower bound)": "cfrp (lower)",
    "cfrp (upper bound)": "cfrp (upper)",
    "gfrp (lower bound)": "gfrp (lower)",
    "gfrp (upper bound)": "gfrp (upper)",
    "wood (// to grain)": "wood (parallel)",
    "wood (-| to grain)": "wood (perpendicular)"
}

# def get_modulus(material):
    # material = get_materials_like(mat_dict[material])[0]
    # return material.youngs_mod

gravity = 9.81


class Beam():
    """ Superclass for simple beams """
    material: Material
    dimensions: dict

    def __init__(self, material, dimensions):
        self.material = material 
        self.dimensions = dimensions
    

class HollowCyl(Beam):
    """ Hollow cylinder beam """
    def __init__(self, material, dimensions, nyvals=1000,*args, **kwargs):        
        super(HollowCyl, self).__init__(material, dimensions)
        self.outer_diam = dimensions['outer_diam']
        self.inner_diam = dimensions['inner_diam']
        self.length = dimensions['length']
        self.ymax = self.length/2
        self.ymin = -self.length/2
        self.I_zz = self._find_I()
        self.J = self._find_J()
        self.volume = self._find_volume()
        self.mass = self.volume * self.material.density if material.density else None
        self.yvals = np.linspace(self.ymin, self.ymax, nyvals)

    def _find_I(self):
        return math.pi/64 * (self.outer_diam**4 - self.inner_diam**4)
    def _find_J(self):
        return math.pi/32 * (self.outer_diam**4 - self.inner_diam**4)
    def _find_volume(self):
        return math.pi/4 * (self.outer_diam**2 - self.inner_diam**2) * self.length
        

def get_elliptic_lift_fn(beam, lift_tot):
    """ Given a beam corresponding to a wing and the total lift, returns a function of y 
    corresponding to an elliptic lift distribution over y. """
    ellipse = lambda y: np.sqrt(1 - (2*y)**2) # from -1/2 to 1/2
    # find lift at midpoint (0.785 = area under ellipse(y) )
    lift_0 = lift_tot/(beam.length * 0.785398163397448)
    scaled_ellipse = lambda y: lift_0 * ellipse(y/beam.length)
    return scaled_ellipse

def find_weight(mass, num_gs):
    """ Find the effective weight of a mass accelerating at `num_gs` times the acceleration due to gravity"""
    return mass * num_gs * gravity

def find_loading(W, beam):
    """ Given a centered array of y-values, returns the loading distribution over the wing """
    # model elliptic lift over the wing
    lift = get_elliptic_lift_fn(beam,W)
    loading = lift(beam.yvals)
    # model airplane weight as a delta function at y=0
    loading[len(loading)//2] -= np.sum(loading)
    return loading

def integrate_arr(array, beam):
    """ Integrates an array of values over the wing """
    return integrate.cumulative_trapezoid(array, beam.yvals[:len(array)])


def find_shear(loading, beam):
    """ Finds shear given loading conditions """
    shear = integrate_arr(loading, beam)
    # free end boundary condition
    shear -= shear[0]
    return shear

def find_moment(shear, beam):
    """ Finds moment acting on the wing given shear """
    moment = integrate_arr(shear, beam)
    # free end boundary condition
    moment -= moment[0]
    return moment

def find_angle(moment, beam):
    """ Finds the y-relative angle of the wing given moment """
    # angle of beam at given moment
    theta = integrate_arr(moment, beam)
    theta /= (beam.I_zz * beam.material.get_youngs_mod())
    # fixed center boundary condition
    theta -= theta[len(theta)//2]
    return theta

def find_displacement(theta, beam):
    """ Finds the vertical displacement of the wing given angle """
    # vertical displacement
    disp = integrate_arr(theta, beam)
    # fixed center boundary condition
    disp -= disp[len(disp)//2]
    return disp

def plot_data(ax, y, data, color="black", xlabel="y distance", ylabel=""):
    ax.plot(y, data, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

def make_all_charts(axs, loading, beam):
    """ Makes all charts for a given wing """
    shear = find_shear(loading, beam)
    moment = find_moment(shear, beam)
    angle = find_angle(moment, beam)
    disp = find_displacement(angle, beam)
    y = beam.yvals
    plot_data(axs[0,0], y[:-1], shear, ylabel="shear (N)")
    plot_data(axs[1,0], y[:-2], moment, ylabel="moment (N.m)")
    plot_data(axs[0,1], y[:-3], angle * 180 / math.pi, ylabel="angle (deg)")
    plot_data(axs[1,1], y[:-4], disp * 1e3, ylabel="displacement (mm)")
    # axs[0,0].axis([min(y)-0.5, max(y)+0.5, -1, max(loading)])

def get_parameters(material, outer_diam, inner_diam, b, W, gs):
    weight = find_weight(W, gs)
    dimensions = {"outer_diam":outer_diam, "inner_diam":inner_diam, "length":b}
    beam = HollowCyl(material, dimensions)
    loading = find_loading(weight, beam)
    return {"beam": beam, "loading": loading}

if __name__ == "__main__":
    dimensions = {"outer_diam": 0.030, "inner_diam": 0.027, "length":2.4}
    material = get_materials_like("cfrp")[0]
    beam = HollowCyl(material, dimensions)
    loading = find_loading(find_weight(3, 6), beam)
    fig, axs = plt.subplots(2,2)
    make_all_charts(axs, loading, beam)
    plt.show()