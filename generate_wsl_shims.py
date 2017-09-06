import os
import sys
import glob

# use activate.bat to maximise the chance the environment is set up correctly in Windows-land
SHIM_TEMPLATE = '#!/bin/sh\n' \
'# WSL shim to launch __EXE_NAME__\n' \
'cmd.exe /C "__BASE_FOLDER__\\activate.bat && __BASE_FOLDER__\\__EXE_NAME__ $@"' '\n'

def gen_shims(env_dir):
    for file in glob.glob(os.path.join(env_dir, 'Scripts','*.exe')):
        full_exe_path = os.path.abspath(file)
        
        full_path, exe_name = os.path.split(full_exe_path)
        shim_path, ext = os.path.splitext(full_exe_path)
        
        shim_contents = SHIM_TEMPLATE.replace('__EXE_NAME__',exe_name).replace('__BASE_FOLDER__',full_path).replace('\\','\\\\')
        
        with open(shim_path, 'w', newline='\n') as f:
            f.write(shim_contents)

def patch_activate(env_dir):
    activate_path = os.path.join(env_dir, 'Scripts','activate')
    
    with open(activate_path, 'r', newline='\n') as f:
        contents = f.read()
        
        path_components = os.path.abspath(env_dir).split(os.path.sep)
        path_components[0] = path_components[0][:-1].lower()
        
        wsl_path = '/mnt/'+ '/'.join(path_components)
        print(wsl_path)
        # add in a check for bash on WSL and set VIRTUAL_ENV accordingly
        # note the double space in "export  VIRTUAL_ENV" which prevent multiple patches
        contents_patched = contents.replace('export VIRTUAL_ENV',
        'if grep -qE "(Microsoft|WSL)" /proc/version &> /dev/null ; then VIRTUAL_ENV='+wsl_path+'; fi; export  VIRTUAL_ENV')
    with open(activate_path, 'w', newline='\n') as f:
        f.write(contents_patched)

def main():
    if len(sys.argv) < 2:
        print('Usage: generate_wsl_shims.py <path to virtualenv root folder>')
        sys.exit(1)
    dir = sys.argv[1]
    # generate a shim for every exe in the scripts folder (otherwise you need to type python.exe, pip.exe, etc.)
    gen_shims(dir)
    
    # patch the activate script to use WSL path convention if it detects WSL
    # ideally this would just be added to the template in virtualenv
    patch_activate(dir)
    

if __name__ == '__main__':
    main()
