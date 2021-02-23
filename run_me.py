import os
import sys
reqd, to_install = ['sox', 'ffmpeg', 'soundstretch'], []

def err(msg):
    print("Error: " + msg)
    sys.exit(1)

def run(cmd):
    print("> " + cmd)
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd)

def is_installed(cmd):
    where = os.popen("which " + cmd).read().strip()
    return os.path.exists(where)

for req in reqd: # check each req'd terminal command
    if not is_installed(req):
        req = "soundtouch" if req == "soundstretch" else req
        to_install.append(req) # soundstretch command lives in soundtouch

def install(cmd): # install a terminal command
    my_os = os.popen("uname").read().strip()
    
    if my_os == 'Linux':
        cmd = 'sudo apt install ' + cmd
    elif my_os == 'Darwin':
        if is_installed("brew"):
            cmd = 'sudo brew install ' + cmd
        elif is_installed("port"):
            cmd = 'sudo port install ' + cmd
        else:
            err("neither brew nor port package-manager detected. Please install one and try again!")
    else:
        err("os: " + my_os + " not supported yet, sorry!")

    print("attempting to install " + cmd + " with command:")
    print("\t" + cmd)

    run(cmd)

for req in to_install:
    install(req)
