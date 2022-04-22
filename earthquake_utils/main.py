# main.py by Konov Denis,
# telegram: @stdio, mail: konov1999@gmail.com 
#
# Generates data for neural network experiments
# version 0.1, apr 2022

from composer5 import *
import subprocess
import random
import os
import sys

# -----------------------
# PROBLEM WIDE PARAMETERS
# -----------------------

# Default path to the compute environment
def_path = str(os.curdir)
# Default path to save csv
csv = def_path + "\\csv"
# Default path of the swift environment
env = def_path + "\\env"
# Min inner edge
edge = int(30)
# Time period to compute
time = 1.5
# Elastic characteristics (rho, v1, v2)
elastic = (2400, 4300, 2400)
# Geometry of body (len, height)
body_dimensions = (6000, 1550)
# Receivers x left and right coordinate,
rec_len = int(2000) # Value will be doubled ( considered as [-len;+len] segment )
rec_step = int(40)
# Initial state of the wave
inistate = {
        "inistate": "wave",
        "inistate velocity": "0 -1",
        "inistate er": "100",
        "inistate ecentre": "0 -100",
}
# Number of problems to calculate
num = 600

# -----------------------------
# SINGLE CALCULATION PARAMETERS
# -----------------------------

# A path to difference csv file
# "None" to disable, "Auto" to generate before calculations
# def_path + "\\diff.csv"
difference = "Auto"  
# X segment (coordinates of the crack array)
x = (-2000, 2000)
# Z segment (depth of the crack (lowest point for a = 90))
z = (700, 1500)
# a segment (angle between ox and crack)
a = (75, 105)
# h segment (height of the crack)
h = (60, 300)


# Probability function (uniform)
def uni(segment):
    return random.uniform(segment[0], segment[1])


def generate(body, environment):
    body.clear_features()
    xx = uni(x)
    zz = uni(z)
    aa = uni(a)
    hh = uni(h)
    body.add_feature([(xx, -zz)], "Empty", aa, hh)
    environment.write(env)
    return "_x=%f_z=%f_a=%f_h=%f" % (xx, zz, aa, hh)


def calc(body, environment, name):
    name += generate(body, environment)
    # print("[NOTICE] Calling earthquake: " + env + "\\earthquake.exe")
    subprocess.call(env + "\\earthquake.exe", shell=True)
    if os.stat(env + "\\earthquake.log").st_size == 0:
        print("[ERROR] Error occurred at computation %s" % name)
        exit(-1)
    else:
        if difference == "Auto":
            subprocess.call('csv_difference.exe ' +
                            env + '\\receivers.csv ' +
                            def_path + '\\base.csv ' +
                            csv + '\\%s.csv ' % name, shell=True)
        elif difference != "None":
            subprocess.call('csv_difference.exe ' +
                            env + '\\receivers.csv ' +
                            difference + ' ' +
                            csv + '\\%s.csv ' % name, shell=True)
        else:
            os.replace(env + '\\receivers.csv', csv + '\\%s.csv' % name)
    print("[NOTICE] %s.csv OK" % name)


def main():
    debug = open("composer5.log", "w")
    sys.stdout = debug
    print("[NOTICE] Started execution. Working directories", "csv = %s" % csv, "env = %s" % env)
    random.seed()

    # Setting up environment
    e = Environment(inistate=inistate)
    e.set_var("max time", str(time))
    e.set_var("min inner edge length", str(edge))
    e.add_receivers(line(-rec_len, rec_len, rec_step, 0))
    b = Body(int(elastic[0]), int(elastic[1]), int(elastic[2]))
    b.add_geometry(rect(body_dimensions[0], -body_dimensions[1]))
    e.add_body(b)

    # Empty calculation
    print("[NOTICE] Carrying out preliminary empty medium computation")
    b.clear_features()
    e.write(env)
    subprocess.call(env + "\\earthquake.exe", shell=True)
    if os.stat(env + "\\earthquake.log").st_size == 0:
        print("[ERROR] Error occurred at preliminary empty medium computation")
        exit(-1)

    os.replace(env + '\\receivers.csv', def_path + '\\base.csv')

    # Computing
    for i in range(1, num+1):
        calc(b, e, str(i))

    debug.close()


if __name__ == "__main__":
    main()
