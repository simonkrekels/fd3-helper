import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import glob
import os

'''
v1.0
A simple script to quickly view data coming from popular filetypes
when using fd3

v1.1
Now gives the option to change directory first
'''


def modfig():

    # Select correct file
    print('\nLoading filenames...')
    filenames = glob.glob('*.mod')
    filenames.sort()

    if len(filenames) == 0:
        print('No files of chosen filetype found.')
        typepicker()

    for i in range(len(filenames)):
        print(str(i) + ': ' + filenames[i])

    n = int(input("Choose file: "))

    if n not in range(len(filenames)):
        print("\n### Invalid file chosen. Returning to start... ###\n")
        typepicker()

    name = filenames[n]

    # Load data
    try:
        mod = np.loadtxt(name).transpose()
        w = np.exp(mod[0])  # Convert back to wavelength space

        spec1 = mod[1]
        spec2 = mod[2]

        if mod.shape[0] != 3:
            print("\n### This file format can't be handled ###\n")
            typepicker()

    except (IndexError, ValueError):
        print("\n### This file format can't be handled ###\n")
        typepicker()

    norm = input("\nNormalise each spectrum? (Y/N): ")
    while norm not in ('y', 'Y', 'N', 'n'):
            norm = input("\nNormalise each spectrum? (Y/N): ")

    if norm in ('y', 'Y'):
        # Plot figure
        plt.figure()

        plt.plot(w, spec2 / np.mean(spec2[0:20]), 'C0')
        plt.plot(w, spec1 / np.mean(spec1[0:20]), 'C3')


        plt.show()
    else:
        # Plot figure
        plt.figure()

        plt.plot(w, spec2, 'C0')
        plt.plot(w, spec1, 'C3')
        plt.title('fd3 result; entire spectrum, 107 split points')
        plt.ylabel('normalised flux', fontdict=None, labelpad=None)
        plt.xlabel(r'$\lambda\,[\AA]$', fontdict=None, labelpad=None)

        plt.show()

    typepicker()


def txtfig():
    # Select correct file
    print('\nLoading filenames...')
    filenames = glob.glob('*.txt')
    filenames.sort()

    if len(filenames) == 0:
        print('No files of chosen filetype found.')
        typepicker()

    for i in range(len(filenames)):
        print(str(i) + ': ' + filenames[i])

    n = int(input("Choose file: "))

    if n not in range(len(filenames)):
        print("\n### Invalid file chosen. Returning to start... ### \n")
        typepicker()

    name = filenames[n]

    # Load data
    try:
        txt = np.loadtxt(name).transpose()
        w = txt[0]
        if txt[0][0] < 1000:
            w = np.exp(txt[0])
        Intensity = txt[1]

        if txt.shape[0] != 2:
            print("\n### This file format can't be handled ###\n")
            typepicker()

    except (IndexError, ValueError):
        print("\n### This file format can't be handled ###\n")
        typepicker()

    # Plot figure
    plt.figure()

    plt.plot(w, Intensity)

    plt.show()

    typepicker()


def scale_raw_spectra(w, f, window=[7500, 7550]):
    inds = [i for i in range(len(w)) if window[0] <= w[i] <= window[1]]
    return f / np.mean(f[inds])


def fitsfig():
    # Select correct file
    print('\nLoading filenames...')
    filenames = glob.glob('*.fits')
    filenames.sort()

    if len(filenames) == 0:
        print('No files of chosen filetype found.\n')
        typepicker()

    for i in range(len(filenames)):
        print(str(i) + ': ' + filenames[i])

    n = int(input("Choose file: "))

    if n not in range(len(filenames)):
        print("\n### Invalid file chosen. Returning to start... ### \n")
        typepicker()

    name = filenames[n]

    # Load data
    h = fits.open(name)
    flux = h[0].data

    n_points = h[0].header['NAXIS1']
    start_w = h[0].header['CRVAL1']
    delta_w = h[0].header['CDELT1']

    w = np.exp(np.linspace(start_w,
                           start_w + (delta_w * (n_points - 1)),
                           n_points))

    scaled_f = scale_raw_spectra(w,flux)

    # Plot figure
    plt.figure()

    plt.plot(w, scaled_f)

    plt.show()

    typepicker()


def typepicker():
    print("\nChoose filetype: \n0: .txt (2 columns)\n"
          "1: .mod (3 columns)\n2: .fits\n\nPress 'q' to quit\n")
    chosentype = input('-> ')

    while chosentype not in ('0', '1', '2', 'q', 'h'):
        print("\nChoose filetype: \n0: .txt (2 columns)\n"
              "1: .mod (3 columns)\n2: .fits\n\nPress 'q' to quit\n")
        chosentype = input('-> ')

    if chosentype == '0':
        txtfig()
    elif chosentype == '1':
        modfig()
    elif chosentype == '2':
        fitsfig()
    elif chosentype == 'q':
        raise SystemExit
    elif chosentype == 'h':
        help()
        typepicker()


def help():
    print("""\n### Help for file2fig.py v1.1 ###

    .txt files

        - Expected: 2 columns of data with wavelengths in the first column.

    .mod files

        - Expected: 3 columns of data with wavelengths in the first column
                    and intensities in 2nd and 3rd columns.

        - .mod files generatde by fd3 should work fine.

    .fits files

        - Should always work (not sure though)

        """)


def path_chooser():
    '''
    cwd -> current working directory
    lsdir -> all available subdirectories
    '''
    cwd = os.getcwd()
    lsdir = glob.glob('*/')

    print("\n### Select a directory ###\n")
    print("0 Current: " + cwd)

    for i in range(1, len(lsdir) + 1):
        print(str(i) + ' ' + lsdir[i - 1])

    print(str(len(lsdir) + 1) + " One up")

    n = int(input("\n-> "))

    while n != 0:
        if n == len(lsdir) + 1:
            os.chdir("..")
        else:
            os.chdir(cwd + '/' + lsdir[n - 1])

        cwd = os.getcwd()
        lsdir = glob.glob('*/')

        print("\n### Select a directory ###\n")
        print("0 Current: " + cwd)

        for i in range(1, len(lsdir) + 1):
            print(str(i) + ' ' + lsdir[i - 1])

        print(str(len(lsdir) + 1) + " One up")

        n = int(input("\n-> "))

    return os.getcwd()


def main():
    dirchoice = input("\nWork in current directory? (Y/N): ")
    while dirchoice not in ('Y', 'y', 'N', 'n', 'h'):
        print("\nPlease enter 'y' or 'n'")

        dirchoice = input("\nWork in current directory? (Y/N): ")
    if dirchoice == 'n' or dirchoice == 'N':
        path_chooser()
        typepicker()
    elif dirchoice == 'h':
        help()
        main()
    else:
        typepicker()


print("""
### file2fig v1.1 ###

Press 'h' at any prompt for help concerning
formatting expectations for data files. """)

main()
