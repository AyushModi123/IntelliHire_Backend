import subprocess

# Command to install Python dependencies using pip
pip_install_command = ['pip', 'install', '-r', 'requirements.txt']

# Command to install sqlite-devel using yum
yum_install_command = ['yum', 'install', 'sqlite-devel']

# Execute pip install command
try:
    subprocess.run(pip_install_command, check=True)
    print("Python dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print("Error installing Python dependencies:", e)

# Execute yum install command
try:
    subprocess.run(yum_install_command, check=True)
    print("sqlite-devel installed successfully.")
except subprocess.CalledProcessError as e:
    print("Error installing sqlite-devel:", e)
