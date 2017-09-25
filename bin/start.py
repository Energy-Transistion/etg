#!python3
# pylint: disable=invalid-name

from os import chdir, execv, getenv, path, pathsep, putenv

realpath = path.realpath(__file__)
main_dir = path.dirname(path.dirname(realpath))
print("Running the ETG from " + main_dir)
venv = path.join(main_dir, 'venv')
if path.exists(path.join(venv, 'bin')):
    bin_dir = 'bin'
else:
    bin_dir = 'Scripts'
twistd = path.join(venv, bin_dir, 'twistd')
print(twistd)
old_path = getenv('PYTHONPATH')
if old_path:
    putenv('PYTHONPATH', main_dir + pathsep + getenv('PYTHONPATH'))
else:
    putenv('PYTHONPATH', main_dir)
#chdir(main_dir)
execv(twistd, ['twistd', '-ny', path.join(main_dir, 'bin', 'test-server')])
