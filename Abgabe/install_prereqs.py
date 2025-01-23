import os, sys
import subprocess

python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
target = os.path.join(sys.prefix, 'lib', 'site-packages')

subprocess.call([python_exe, '-m', 'ensurepip'])
subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'Pillow', '-t', target])
subprocess.call([python_exe, '-m', 'pip', 'install', 'shapely', '-t', target])
subprocess.call([python_exe, '-m', 'pip', 'install', 'opencv-python', '-t', target])
subprocess.call([python_exe, '-m', 'pip', 'install', 'centerline', '-t', target])