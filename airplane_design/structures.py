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

    def __init__(self, material, dimensions, nyvals=1000):
        self.material = material 
        self.dimensions = dimensions
        self.nyvals = nyvals
    

class HollowCyl(Beam):
    """ Hollow cylinder beam """
    def __init__(self, material, dimensions,*args, **kwargs):        
        super(HollowCyl, self).__init__(material, dimensions, *args, **kwargs)
        self.outer = dimensions['outer']
        self.inner = dimensions['inner']
        self.length = dimensions['length']
        self.ymax = self.length/2
        self.ymin = -self.length/2
        self.I_x = self._find_I()
        self.I_y = self._find_I()
        self.J_z = self._find_J()
        self.volume = self._find_volume()
        self.mass = self.volume * self.material.get_density() if self.material.get_density() else 0
        self.yvals = np.linspace(self.ymin, self.ymax, self.nyvals)
        self.section_modulus = self.I_x / (self.outer/2)

    def _find_I(self):
        return math.pi/64 * (self.outer**4 - self.inner**4)
    def _find_J(self):
        return math.pi/32 * (self.outer**4 - self.inner**4)
    def _find_volume(self):
        return math.pi/4 * (self.outer**2 - self.inner**2) * self.length

class HollowSquare(Beam):
    """ Hollow square beam """
    def __init__(self, material, dimensions, *args, **kwargs):
        super(HollowSquare, self).__init__(material, dimensions, *args, **kwargs)
        self.outer_width = dimensions['outer']
        self.inner_width = dimensions['inner']
        self.length = dimensions['length']
        self.ymax = self.length/2
        self.ymin = -self.length/2
        self.I_x = self._find_I()
        self.I_y = self._find_I()
        self.J_z = self._find_J()
        self.volume = self._find_volume()
        self.mass = self.volume * self.material.get_density() if material.get_density() else 0
        self.yvals = np.linspace(self.ymin, self.ymax, self.nyvals)
        self.section_modulus = self.I_x / (self.outer_width/2)
    
    def _find_I(self):
        return 1/12 * (self.outer_width**4 - self.inner_width**4)
    def _find_J(self):
        return self.I_x + self.I_y
    def _find_volume(self):
        return (self.outer_width**2 - self.inner_width**2) * self.length

beam_dict = {
    "Hollow Cylinder": HollowCyl,
    "Hollow Square": HollowSquare
}

def get_elliptic_lift_fn(beam, lift_tot):
    """ Given a beam corresponding to a wing and the total lift, returns a function of y 
    corresponding to an elliptic lift distribution over y. """
    ellipse = lambda y: np.sqrt(1 - (2*y)**2) # from -1/2 to 1/2
    # find lift at midpoint (0.785 = area under ellipse(y) )
    lift_0 = lift_tot/(beam.length * 0.785398163397448)
    scaled_ellipse = lambda y: lift_0 * ellipse(y/beam.length)
    return scaled_ellipse

def find_weight(mass, gforce):
    """ Find the effective weight of a mass accelerating at `gforce` times the acceleration due to gravity"""
    return mass * gforce * gravity

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
    theta /= (beam.I_x * beam.material.get_youngs_mod())
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

def solve_system(loading, beam):
    """ Solves the system of equations for shear, moment, angle, and displacement """
    shear = find_shear(loading, beam)
    moment = find_moment(shear, beam)
    angle = find_angle(moment, beam)
    disp = find_displacement(angle, beam)
    max_stress = max(moment) / beam.section_modulus
    return {
        "beam": beam,
        "loading": loading,
        "shear": shear,
        "moment": moment,
        "angle": angle,
        "displacement": disp,
        "max_stress": max_stress
    }

def get_system_info(system):
    max_moment = max(system['moment'])
    max_displacement = max(system['displacement'])
    max_stress = max_moment / system['beam'].section_modulus
    return {
        "max_moment": max_moment,
        "max_displacement": max_displacement,
        "max_stress": max_stress
    }


def plot_data(ax, y, data, color="black", xlabel="y distance", ylabel=""):
    ax.plot(y, data, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

def make_all_charts(axs, system):
    """ Makes all charts for a given wing """
    y = system['beam'].yvals
    plot_data(axs[0,0], y[:-1], system['shear'], ylabel="shear (N)")
    plot_data(axs[1,0], y[:-2], system['moment'], ylabel="moment (N.m)")
    plot_data(axs[0,1], y[:-3], system['angle'] * 180 / math.pi, ylabel="angle (deg)")
    plot_data(axs[1,1], y[:-4], system['displacement'] * 1e3, ylabel="displacement (mm)")
    # axs[0,0].axis([min(y)-0.5, max(y)+0.5, -1, max(loading)])

def get_system(material_name, dimensions, W, gforce, beamtype):
    material = get_materials_like(material_name)[0]
    weight = find_weight(W, gforce)
    beam = beamtype(material, dimensions)
    loading = find_loading(weight, beam)
    system = solve_system(loading, beam)
    return system

if __name__ == "__main__":
    dimensions = {"outer": 0.030, "inner": 0.027, "length":2.4}
    material = get_materials_like("cfrp")[0]
    beam = HollowCyl(material, dimensions)
    loading = find_loading(find_weight(3, 6), beam)
    system = solve_system(loading, beam)
    fig, axs = plt.subplots(2,2)
    make_all_charts(axs, system)
    plt.show()