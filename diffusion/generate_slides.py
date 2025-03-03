
def write_opening_slides(out_file):
    out_file.write("\\documentclass{beamer}\n")
    out_file.write("\\title{Scatter plot time evolutions}\n")
    out_file.write("\\author{Duncan Leggat}\n")
    out_file.write("\\institute{UCL}\n")
    out_file.write("\\date{\today}\n")
    out_file.write("\n\\begin{document}\n")

def close_slides(out_file):
    out_file.write("\\end{document}\n")

def begin_slide(out_file):
    out_file.write("\\begin{frame}\n")

def end_slide(out_file):
    out_file.write("\\end{frame}\n")
    
def write_single_slide_time_evo(out_file,cube_name,layer,timesteps):
    begin_slide(out_file)
    cube_name_title = "-".join(cube_name.split("_"))
    out_file.write(f"\\frametitle{{{cube_name_title} at layer {layer}}}\n")
    plot_n = 0
    for timestep in timesteps:
        plot_n+=1
        end_line = ""
        if plot_n%3 == 0: end_line = "\\\\"
        #        out_file.write(f"\\includegraphics[width=0.32\\textwidth]{{{cube_name}-level{layer}-{timesteps:04d}_steps_before_crash.png}} {end_line}\n")
        out_file.write(f"\\includegraphics[width=0.32\\textwidth]{{{cube_name}-level{layer}-{timestep:04d}_steps_before_crash.png}} {end_line}\n")
    end_slide(out_file)
        
def main():

    cubes = {
        "eastward_wind": [50,51,53,56,66],
        "dtheta_slow": [50,60,63,64,65,66],
    }
    timesteps = [0,20,50,100,200,300,1000]

    with open("map_presentation.tex","w") as f:
        
        write_opening_slides(f)
        
        for cube in cubes:
            for layer in cubes[cube]:
                write_single_slide_time_evo(f,cube,layer,timesteps)
        close_slides(f)
    
if __name__ == "__main__":
    main()
