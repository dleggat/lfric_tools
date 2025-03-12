#from tqdm.notebook import tqdm

from functools import partial

import math

import iris
import iris.coord_systems
import iris.fileformats
import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.colors as mcol
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
import numpy as np

def plot_dtheta_trace(cube,coords,label,n_timesteps):

    #   print(cube)
    print(label)
    print(cube.coords("latitude"))
    print(cube.coords("longitude"))

    cube_single_node = cube.extract(iris.Constraint(**coords))

#    print(cube_single_node)

    print(cube_single_node.coords("latitude"))
    print(cube_single_node.coords("longitude"))
    
    tslice = slice(-n_timesteps,None,None)
    
 #   print(cube_single_node)

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
        cube_single_node.data[tslice,...].T
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
    
#    plt.show()

def make_scatter_plot(cube,timestep,layers, plot_label):


    print(plot_label)
    fig,ax = plt.subplots()

    cube_single_level = cube.extract(iris.Constraint(**layers))

#    print(cube_single_level)

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

    ax.set_title(f"{plot_label}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.savefig(f"{plot_label}.png")


def make_line_plot_one_point(cube,location,layers,plot_label):

    print(f"Line plot {plot_label}")
    
    fig,ax = plt.subplots()
    cube_slimmed = cube.extract(iris.Constraint(**location,**layers))

    print(cube_slimmed.data.T)

    plt.plot(cube_slimmed.data.T)

    ax.set_xlabel("Timestep")
    ax.set_title(plot_label)

    plt.savefig(f"{plot_label}_time_plot.png")

    ax.set_yscale('log')

    plt.savefig(f"{plot_label}_time_plot_log.png")

def make_multiline_plot(cube, locations, layers, plot_label):

    print(f"Making multi-line {plot_label}")

    fig,ax = plt.subplots()

    max = 1.
    min = 0.

    for location_name,location in locations.items():
        print(location_name)
        cube_slimmed = cube.extract(iris.Constraint(**location,**layers))
        plt.plot(cube_slimmed.data.T, label=location_name)


    ax.set_title(plot_label)
    ax.set_xlabel("Timestep")
    plt.legend()
    plt.savefig(f"{plot_label}_overlayed_plot.png")

def calculate_temp_cube(exner,potent,layer):
    layer_exner = exner.extract(iris.Constraint(**{"half_levels":layer}))
    layer_potent_up = potent.extract(iris.Constraint(**{"full_levels":layer+0.5}))
    layer_potent_down = potent.extract(iris.Constraint(**{"full_levels":layer-0.5}))

    layer_potent = (layer_potent_up + layer_potent_down)/2.

    temp = layer_potent * layer_exner

    return temp


def within_limits(number,max,min):
    if number < max and number > min: return True
    return False
    
def main(max_timestep, locations, cubes_of_interest):

 
    print(cubes_of_interest)

    # Make the trace plots
    for loc_label, coords in locations.items():
        for cube_label, cube in cubes_of_interest.items():
            plot_label = f"{cube_label}-{loc_label}"
            plot_dtheta_trace(cube,coords,plot_label,100)

    # Make some scatter plots.
    levels_of_interest = {
        "dtheta_slow": ["full_levels",[66,65,64,63,60,50]],
        "eastward_wind": ["half_levels", [65.5,50.5,52.5,55.5,49.5]],
    }

    # The first one is timesteps leading up to crash, the second is from the beginning
    timesteps_of_interest = [0,20,50,100,200,300,1000]
#    timesteps_of_interest = [max_timestep,max_timestep-20,max_timestep-50,max_timestep-100,max_timestep-200,max_timestep-500]
    for timestep in timesteps_of_interest:
        for cube_name, level_deets in levels_of_interest.items():
            for level in level_deets[1]:
                plot_label = f"{cube_name}-level{math.ceil(level):02d}-{timestep:04d}_steps_before_crash"
                plot_label = f"{cube_name}-level{math.ceil(level):02d}-{max_timestep-timestep:04d}_steps_from_zero"
                make_scatter_plot(cubes_of_interest[cube_name],max_timestep-timestep,{level_deets[0]:level},plot_label)

    # Set to the levels you want the plots for
    level_of_interest = {
        "dtheta_slow": ["full_levels",[66,50]],
        "potential_temp": ["full_levels",[66,50]],
        "exner_pressure": ["half_levels",[65.5,49.5]],
        }

    cubes_of_interest["potential_temp"] = cubes.extract_cube("air_potential_temperature")
    for loc_name,location in locations.items():
        for cube_name, level_deets in level_of_interest.items():
            for level in level_deets[1]:
                plot_label = f"{cube_name}-level{math.ceil(level):02d}-{loc_name}"
                make_line_plot_one_point(cubes_of_interest[cube_name],location,{level_deets[0]:level},plot_label)

    # layered plots for level of interest plots
    for cube_name, level_deets in level_of_interest.items():
        for level in level_deets[1]:
            plot_label = f"{cube_name}-level{math.ceil(level):02d}"
            make_multiline_plot(cubes_of_interest[cube_name],locations,{level_deets[0]:level},plot_label)
        
    exner = cubes.extract_cube("exner_pressure")
    potent = cubes.extract_cube("air_potential_temperature")

    # Makes real temp plots for the following layers
    real_temp_levels = [65.5, 49.5]
    for real_temp_level in real_temp_levels:
        temp = calculate_temp_cube(exner,potent,real_temp_level)
        plot_label = f"real-temp_level{math.ceil(real_temp_level):02d}"
        print(temp)
        make_multiline_plot(temp,locations,{"half_levels":real_temp_level},plot_label)

if __name__ == "__main__":
    in_cube = "lfric_diag.nc"
    cubes = iris.load(in_cube)

    print (cubes)

    cubes_of_interest = {
        "dtheta_slow": cubes.extract_cube("potential_temperature_increment_from_slow_physics"),
        "eastward_wind": cubes.extract_cube("eastward_wind"),
        "exner_pressure": cubes.extract_cube("exner_pressure"),
    }

    # Set the timestep before the crash, here!
    #    max_timestep = 2007 #run57
    max_timestep = 3132 # run53
    #    max_timestep = 2031 #run54

    # Locations
    locations = {
#        "crash":{"longitude":partial(within_limits,max=149.,min=148.),"latitude":partial(within_limits,max=11.5,min=10.5)}, #run54 - temp on, wind off
#        "crash":{"longitude":partial(within_limits,max=164.,min=163.),"latitude":partial(within_limits,max=9.,min=8.5)}, #run53 - temp on, wind on
#        "crash_neg":{"longitude":partial(within_limits,max=164.,min=163.),"latitude":partial(within_limits,max=-5.,min=-5.4)}, #run53
#        "crash":{"longitude":partial(within_limits,max=144.5,min=144.),"latitude":partial(within_limits,max=-7,min=-8)}, #run57 - temp off, wind off
#        "crash":{"longitude":partial(within_limits,max=167.,min=166.),"latitude":partial(within_limits,max=2.,min=1.8)}, #run61 - temp off, wind on
        "ssp":{"longitude":partial(within_limits,max=0.,min=-3.),"latitude":partial(within_limits,max=0.,min=-3.)},
#        "random":{"longitude":partial(within_limits,max=-19,min=-21),"latitude":partial(within_limits,max=-19,min=-21)}, # commenting because too similar
        "asp":{"longitude": partial(within_limits, max=180., min=178.), "latitude": partial(within_limits, max=0., min=-3.)},
        "terminator":{"longitude": partial(within_limits, max=92., min=89.), "latitude": partial(within_limits, max=0., min=-3.)},
    }
    
    main(max_timestep, locations, cubes_of_interest)

    
