#!python3
# pylint: disable=invalid-name

from os import path
from subprocess import call
from sys import executable

print("Installing the ETG.")
real_path = path.realpath(__file__)
print("Realpath:\t" + real_path)
main_dir = path.dirname(path.dirname(real_path))
print("Installing into " + main_dir)
venv = path.join(main_dir, 'venv')
print("Putting dependencies into " + venv)
print("Setting up the virtual environment")
call(executable + ' -m venv "' + venv + '"', shell=True)
if path.exists(path.join(venv, 'bin')):
    bin_dir = 'bin'
else:
    bin_dir = 'Scripts'
pip = path.join(venv, bin_dir, 'pip')
print(pip)
# Cause Windows is retarded or something
if not path.exists(pip):
    call('"' + path.join(venv, bin_dir, 'python') + '" -m ensurepip --default-pip', shell=True)
requirements = path.join(main_dir, 'requirements', 'base.txt')
print(requirements)
print("Installing the requirements")
call('"' + pip + '" install -r "' + requirements + '"', shell=True)
print("Done!")
