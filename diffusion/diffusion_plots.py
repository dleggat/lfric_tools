
from functools import partial

import iris
import iris.coord_systems
import iris.fileformats
import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.colors as mcol
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np


def plot_dtheta_trace(cube,coords,label,n_timesteps):

    cube_single_node = cube.extract(iris.Constraint(**coords))

    print(cube_single_node.coords("latitude"))
    print(cube_single_node.coords("longitude"))
    
    tslice = slice(-n_timesteps,None,None)
    
    print(cube_single_node)

#    print(cube_single_node.data[tslice,...].T)

    fig,ax = plt.subplots()

    t_points = np.arange(n_timesteps)
    z_points_ref = "full_levels"
    try:
        cube_single_node.coord("full_levels")
    except:
        z_points_ref = "half_levels"
    z_points = cube_single_node.coord(z_points_ref).points
    
    
    _p0 = ax.pcolormesh(
        t_points,
        z_points,
        cube_single_node.data[tslice,...].T[1]
    )

    ax.set_title(f"{label}")
    ax.set_xlabel("Timesteps before crash")
    ax.set_ylabel("Levels")

    xticks = np.concatenate(
        [
            np.arange(0,n_timesteps+1),
        ]
    )
    ax.set_xticklabels(xticks - n_timesteps)

    cbar = fig.colorbar(_p0, ax=ax)
    
    plt.savefig(f"{label}.png")
    
    plt.show()


def make_scatter_plot(cube,timestep,layers):

    fig,ax = plt.subplots()

    cube_single_level = cube.extract(iris.Constraint(**layers))

    print(cube_single_level)
    
    time_step_cube = cube_single_level[timestep,...]
    lons = time_step_cube.coord("longitude").points
    lats = time_step_cube.coord("latitude").points

    _p0 = ax.scatter(
        lons,
        lats,
        c=time_step_cube.data,
        s=16,
    )

    cbar = fig.colorbar(_p0, ax=ax)
    ax.set_title(f"Name")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    plt.show()
    
    
    
def make_mosaic(locations,cubes_of_interest):

    fig = plt.figure(figsize=(20, 9), constrained_layout=True)
    axd = fig.subplot_mosaic(
        [
            "f",
        ]
    )
    
def main(in_cube):
    cubes = iris.load(in_cube)

    print (cubes)

    cubes_of_interest = {
        "dtheta_slow": cubes.extract_cube("potential_temperature_increment_from_slow_physics"),
        "eastward_wind": cubes.extract_cube("eastward_wind"),
    }
    
    locations = {
        "crash":{"longitude":144.374,"latitude":-7.646},
        "ssp":{"longitude":0.,"latitude":0.},
        "random":{"longitude":20.,"latitude":-20.},
    }
    #    for loc_label, coords in locations.items():
    #        for cube_label, cube in cubes_of_interest.items():
    #            plot_dtheta_trace(cube,coords,f"{cube_label}-{loc_label}",6)
    layers = {"full_levels":66}
    make_scatter_plot(cubes_of_interest["dtheta_slow"],3,layers)

if __name__ == "__main__":
    input_cube = "lfric_diag.nc"
    main(input_cube)
