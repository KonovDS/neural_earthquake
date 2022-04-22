# segyconv.py by Konov Denis,
# telegram: @stdio, mail: konov1999@gmail.com 
#
# Swift .csv to seg-y converter
# version 0.4, feb 2022

import segypy as sp
import numpy as np
import sys
import argparse

# dt feature is implemented as average between last and first snapshot
# Vx is assumed to be odd numbered and Vy aka Vz as even numbered columns


def create_parser():
    parser = argparse.ArgumentParser(description='Converting swift .csv files into seg-y.')
    parser.add_argument('filename', metavar='filename.csv', nargs=1,
                        help='a file to convert')
    parser.add_argument('-c', '--columns', choices=['vx', 'vz', 'both'], default='both',
                        help='columns to be converted to individual files.')
    parser.add_argument('-r', '--receivers', nargs=2, default=[0, 0], type=int, metavar=('N', 'M'),
                        help='receivers to be converted from N to M excluding. It is possible to use negative values')
    parser.add_argument('-p', '--prefix', default=str(),
                        help='prefix to be added to output files')
    parser.add_argument('-s', '--split', nargs=2, default=[0, 0], type=int, metavar=('S', 'R'),
                        help='number of recievers R per group to automatically split in S groups. If set --recievers will be ignored')
    parser.add_argument('--nolog', action='store_true', help='disables logging to file')
    return parser


def check_head(head):
    part = head.split(sep=";")
    if part[0] != "Time":
        print("[segyconv.py] CSV header doesn't conform (Time column). SGY files may be nonsense.")
    for x in part[1::2]:
        if x.split()[0] != "Vx":
            print("[segyconv.py] CSV header doesn't conform (Vx columns). SGY files may be nonsense.")
            break
    for x in part[2::2]:
        if x.split()[0] != "Vy":
            print("[segyconv.py] CSV header doesn't conform (Vy aka Vz columns). SGY files may be nonsense.")
            break


def read_csv(path, key, receivers):
    file = open(path, "r")
    head = file.readline()
    # Will only check standard alignment assuming csv are aligned the same way
    check_head(head)
    csv = file.readlines()
    total_time = float(csv[-1].split(sep=";")[0])
    list = []
    if key == "Vx":
        for row in csv:
            list.append((row.split(sep=";")[1::2])[receivers[0]:(None if receivers[1] == 0 else receivers[1])])
            # list.append(row.split(sep=";")[1::2])
    if key == "Vz":
        for row in csv:
            list.append((row.split(sep=";")[2::2])[receivers[0]:(None if receivers[1] == 0 else receivers[1])])
            # list.append(row.split(sep=";")[1::2])

    return np.array(list).astype(float), total_time / len(list)


def convert(csv_filename, sgy_filename, axis, receivers):
    print('[segyconv.py] Trying to open ', csv_filename)
    data, time_step = read_csv(csv_filename, axis, receivers)
    sp.writeSegy(sgy_filename + ".sgy", data, dt=time_step)


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    if not namespace.nolog:
        sys.stdout = open('segyconv.log', 'w')
    if namespace.prefix:
        namespace.prefix += '_'
    print('[segyconv.py] Executing converter with following parameters:')
    print(namespace)
    if namespace.split[0] == 0:
        if 'vx' or 'both' in namespace.columns:
            convert(namespace.filename[0], namespace.prefix + 'vx', 'Vx', namespace.receivers)
        if 'vz' or 'both' in namespace.columns:
            convert(namespace.filename[0], namespace.prefix + 'vz', 'Vz', namespace.receivers)
    if namespace.split[0] != 0:
        for x in range(namespace.split[0]):
            if 'vx' or 'both' in namespace.columns:
                convert(namespace.filename[0], namespace.prefix + ('group_%d_' % x) + 'vx', 'Vx', ((x * namespace.split[1]), ((x + 1) * namespace.split[1])))
            if 'vz' or 'both' in namespace.columns:
                convert(namespace.filename[0], namespace.prefix + ('group_%d_' % x) + 'vz', 'Vz', ((x * namespace.split[1]), ((x + 1) * namespace.split[1])))


if __name__ == "__main__":
    main()
