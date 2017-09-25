#!python3
# pylint: disable=invalid-name

from os import path
from subprocess import call

print("Installing the ETG.")
real_path = path.realpath(__file__)
print("Realpath:\t" + real_path)
main_dir = path.dirname(path.dirname(real_path))
print("Installing into " + main_dir)
venv = path.join(main_dir, 'venv')
print("Putting dependencies into " + venv)
print("Setting up the virtual environment")
call('python3 -m venv ' + venv, shell=True)
pip = path.join(venv, 'bin', 'pip')
print(pip)
requirements = path.join(main_dir, 'requirements', 'base.txt')
print(requirements)
print("Installing the requirements")
call(pip + ' install -r ' + requirements, shell=True)
print("Done!")
