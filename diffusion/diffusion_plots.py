from tqdm.notebook import tqdm

from functools import partial

import esmf_regrid
import iris
import iris.coord_systems
import iris.fileformats
import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.colors as mcol
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np
from esmf_regrid.experimental.unstructured_scheme import (
    MeshToGridESMFRegridder,
    regrid_unstructured_to_rectilinear,
)
from iris.experimental.ugrid import PARSE_UGRID_ON_LOAD

# from iris.experimental import stratify
#from matplotlib.offsetbox import AnchoredText

#import aeolus
#from aeolus.calc import spatial_mean, time_mean, zonal_mean
#from aeolus.const import init_const
#from aeolus.coord import get_cube_rel_days, get_xy_coords, roll_cube_pm180
#from aeolus.io import create_dummy_cube, load_vert_lev
#from aeolus.model import um
#from aeolus.plot import subplot_label_generator, tex2cf_units
#from aeolus.subset import extract_last_n_days
#from ipywidgets import interact


def extract_heating_rates(cl, model_key):
    if model_key == "um":
        dt_bl = cl.extract_cube("change_over_time_in_air_temperature_due_to_boundary_layer_mixing").copy()
        dt_bl.units = f"{1/300} K/s"
        dt_bl.convert_units("K s-1")

        dt_lw_orig = cl.extract_cube("tendency_of_air_temperature_due_to_longwave_heating")
        dt_sw = cl.extract_cube("tendency_of_air_temperature_due_to_shortwave_heating")

        dt_lw = dt_lw_orig.interpolate([(um.t, dt_sw.coord(um.t).points)], iris.analysis.Linear())
        dt_lw.coord(um.fcst_prd).points = dt_sw.coord(um.fcst_prd).points

        dt_rad = dt_lw + dt_sw
        dt_rad.rename("tendency_of_air_temperature_due_to_radiative_heating")
    elif model_key == "lfric":
        dt_bl = cl.extract_cube("temperature_increment_from_bl_scheme").copy()
        dt_bl.units = f"{1/1800} K/s"
        dt_bl.convert_units("K s-1")

        dt_lw = cl.extract_cube("longwave_heating_rate")
        dt_sw = cl.extract_cube("shortwave_heating_rate")

        dt_rad = dt_lw.copy(data=dt_lw.core_data() + dt_sw.core_data())
        dt_rad.rename("radiative_heating_rate")
    return iris.cube.CubeList([dt_bl, dt_sw, dt_lw, dt_rad])

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
    
    
    ax.pcolormesh(
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
    
    plt.savefig(f"{label}.png")
    
    plt.show()
    
    
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
    for loc_label, coords in locations.items():
        for cube_label, cube in cubes_of_interest.items():
            plot_dtheta_trace(cube,coords,f"{cube_label}-{loc_label}",6)
    
if __name__ == "__main__":
    input_cube = "lfric_diag.nc"
    main(input_cube)
