import iris

from pathlib import Path

def gather_cubes(cube_map):
    
    p = Path(".")
    output_base = p / "share" / "output" / "gungho_model"
    for run_path in output_base.iterdir():
        print (run_path)
        in_file = run_path / "results" / "lfric_diag.nc"
        cubes = iris.load(str(in_file))
        for cube_name in cube_map:
            cube_map[cube_name].append(cubes.extract_cube(cube_name))
        

def concatenate_cubes(cube_map):

    out_cubes = iris.cube.CubeList()
    for cube_name,cubes in cube_map.items():
        for cube in cubes:
            cube.remove_coord("forecast_reference_time")
        print(cube_name,cubes)
        iris.util.unify_time_units(cubes)
        iris.util.equalise_attributes(cubes)
        out_cubes.append(cubes.concatenate_cube())
        print(cubes.concatenate_cube())
        print(out_cubes)

    print(out_cubes)
    return out_cubes

def main():
    in_cubes = [
        "exner_pressure",
        "air_potential_temperature",
        "potential_temperature_increment_from_slow_physics",
        "eastward_wind",
        ]
    
    cube_map = {}
    for in_cube in in_cubes:
        cube_map[in_cube] = iris.cube.CubeList()

    gather_cubes(cube_map)

    out_cubes = concatenate_cubes(cube_map)

    print(out_cubes)

#    for out_cube in out_cubes:
    iris.save(out_cubes,"lfric_diag.nc")

    print(cube_map)

if __name__ == "__main__":
    main()
