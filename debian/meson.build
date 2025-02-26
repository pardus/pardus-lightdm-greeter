# Define the output file
output_file = '__version__'

# Define the command to extract the version
cmd = ['bash', '-c', 'head -n 1 changelog | sed "s/.*(//g;s/).*//g" > '+meson.current_build_dir()+'/__version__']

# Create a custom target
run_command(cmd, check:true)

install_data(meson.current_build_dir() / output_file, install_dir : '/usr/share/pardus/pardus-lightdm-greeter')