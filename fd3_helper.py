import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import progressbar
import multiprocessing as mp
'''
v1.0
06/11/2018
This code was written to ease working with fd3. It lets the user choose where
to split the .in file, and generates new .in files accordingly, with
a certain overlap. The tool also proposes to run the generated .in files
through fd3, and averages the overlapping patches.

v1.1
15/11/2018
Now takes the (linearly) weighted average of the overlaps.

v1.2
21/11/2018
Now uses multithreading to speed up fd3 processing.
'''


class PointBrowser(object):
    """
    click anywhere to create split point at that wavelengt h.
    Press 'd' to remove point closest to cursor.
    Press 'w' to save points.
    """

    def __init__(self, fig, w, f1, f2, filepath, width):

        self.lastind = 0
        if width != 0:
            self.vertical_x_cen = list(np.arange(4000, 6850, width))
        else:
            self.vertical_x_cen = []

        self.wavelength = w
        self.flux1 = f1
        self.flux2 = f2
        self.fig = fig

        self.w_min = min(w)
        self.w_max = max(w)
        self.lower_bound = 4000
        self.upper_bound = 6850
        self.filepath = filepath
        self.knot_width = 0.25
        self.knot_half_width = self.knot_width / 2

        plt.title('.in-file splitter')
        self.raw_plot()
        plt.xlim([4000, 6850])

        self.update()

    def raw_plot(self):

        plt.plot(self.wavelength, self.flux1 / np.mean(self.flux1[0:20]),
                 picker=5)
        plt.plot(self.wavelength, self.flux2 / np.mean(self.flux2[0:20]),
                 picker=5)

    def onpress(self, event):
        '''
        d - delete split point closest to cursor
        u - update the user on how many split points have been selected
        e - reads in saved  split points from file called 'splits.txt'
        w - saves split points
        '''
        if self.lastind is None:
            return

        if event.key not in ('d', 'u', 'e', 'w'):
            return

        elif event.key == 'e':
            print('loading split points...')
            try:
                x = np.loadtxt('splits.txt')
                self.vertical_x_cen = list(x)
                self.vertical_x_cen.sort()
                print('success')
            except:
                print('failed')

        elif event.key == 'w':
            # writes splits to file
            print('saving split points...')
            self.vertical_x_cen.sort()
            np.savetxt('splits.txt', self.vertical_x_cen)
            print('succesfully saved split points')

        elif event.key == 'u':
            # updates user on number of split points currently selected
            print(len(self.vertical_x_cen))

        elif event.key == 'd':
            # deletes point closest to cursor
            try:
                xe = event.xdata
                dif = abs(self.vertical_x_cen - xe)
                dif_ind = list(dif).index(min(dif))
                del self.vertical_x_cen[dif_ind]
            except:
                pass

        self.update()

    def onpick(self, event):
        if self.fig.canvas.manager.toolbar._active is None:
            xe = event.xdata
            if self.w_min < xe < self.w_max:
                self.vertical_x_cen.append(xe)
            self.vertical_x_cen = \
                [i for i in self.vertical_x_cen if i is not None]
            self.update()

    def update(self):
        if self.lastind is None:
            return
        try:
            self.knots.remove()
        except:
            pass
        try:
            for i in self.knots:
                i.remove()
        except:
            pass

        self.knots = []
        for i in self.vertical_x_cen:
            self.knot = plt.axvspan(
                i - self.knot_half_width,
                i + self.knot_half_width,
                alpha=0.3, color='red')
            self.knots.append(self.knot)

        self.fig.canvas.draw()


def load_data(filename):
    '''
    Assumes data coming from an .mod file generated by fd3.n
    Data should be structured in 3 columns with wavelength (in Å) in first
    column, and disentangled fluxes in the second and third columns
    '''
    h = np.loadtxt(filename).transpose()
    flux1 = h[1]
    flux2 = h[2]

    wavelength = np.exp(h[0])
    return wavelength, flux1, flux2


def picker(spec_directory):
    # select correct file
    files = glob.glob(spec_directory + '/*.mod')
    files.sort()

    if len(files) == 0:
        print("### Directory doesn't contain normalised spectra!")
        print("Exiting...")
        raise SystemExit
    else:
        print("\n### Select file ###\n")
        for i in range(len(files)):
            print(str(i) + ' ' + files[i])
        n = input("\n-> ")
        while int(n) not in range(len(files)):
            print("\n### Select file ###\n")
            for i in range(len(files)):
                print(str(i) + ' ' + files[i])
            n = input("\n-> ")

    file = files[int(n)]

    fig = plt.figure(1)

    # load data into memory
    wavelength, flux1, flux2 = load_data(file)

    # choose whether to generate equally sapaced split points or not
    splitchoice = input("Generate equally spaced split points? (Y/N): ")
    while splitchoice not in ('Y', 'y', 'N', 'n'):
        splitchoice = input("Generate equally spaced split points? (Y/N): ")
    if splitchoice == 'Y' or splitchoice == 'y':
        width = int(input("\nSplit width: "))
    else:
        width = 0

    # initiate interactive splitpoint browser
    browser = PointBrowser(
        fig, wavelength, flux1, flux2, spec_directory, width)

    fig.canvas.mpl_connect('button_press_event', browser.onpick)
    fig.canvas.mpl_connect('key_press_event', browser.onpress)

    plt.show()


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


def setBounds(file, splits, overlap=0.5):  # overlap editable. in Å.
    # generates a number of .in files according to the provided splits;
    # labels the split files so that they are in order when .sort() is used
    # over their names.

    # edit .in file
    # read original file
    infile = open(file, 'r')
    lines = infile.readlines()
    infile.close()

    # read splits
    bounds = np.loadtxt(splits)
    maxval = modline1 = lines[0].split('  ')[2]

    try:
        n_splits = len(bounds)
    except TypeError:
        n_splits = 1

    digits = len(str(n_splits))

    for k in range(n_splits + 1):

        modline1 = lines[0].split('  ')

        if k == 0:
            try:
                # edit first line
                modline1[2] = str(np.log(bounds[0] + overlap))  # new maximum value
            except IndexError:
                modline1[2] = str(np.log(bounds + overlap))  # new maximum value

        elif k == n_splits:
            try:
                # edit first line
                modline1[1] = str(np.log(bounds[k - 1] - overlap))  # new min value
                modline1[2] = maxval  # new maximum value
            except IndexError:
                modline1[1] = str(np.log(bounds - overlap))  # new min value
                modline1[2] = maxval  # new maximum value

        else:
            # edit first line
            modline1[1] = str(np.log(bounds[k - 1] - overlap))  # new min value
            modline1[2] = str(np.log(bounds[k] + overlap))  # new maximum value

        modline1[3] = 'sig_aql_used_{:0{}d}.obs'.format(k + 1, digits)
        firstline = ''

        for i in range(len(modline1)):
            if i != 0:
                firstline = firstline + '  ' + modline1[i]
            else:
                firstline = modline1[0]

        # edit last line

        modline2 = lines[-2].split('  ')
        modline2[3] = 'sig_aql_{:0{}d}.mod'.format(k + 1, digits)
        modline2[4] = 'sig_aql_{:0{}d}.res'.format(k + 1, digits)
        modline2[5] = 'sig_aql_{:0{}d}.rvs'.format(k + 1, digits)
        modline2[6] = 'sig_aql_{:0{}d}.log'.format(k + 1, digits)
        lastline = ''
        for i in range(len(modline2)):
            if i != 0:
                lastline = lastline + '  ' + modline2[i]
            else:
                lastline = modline2[0]

        # write new file
        newfile = open(file[:-3] + '_split_{:0{}d}.in'.format(k + 1, digits), 'w')
        newfile.write(firstline)  # write edited line
        for i in range(1, len(lines) - 2):  # write original lines
            newfile.write(lines[i])
        newfile.write(lastline)  # write edited line
        newfile.write('\n')


def select_bounds_file():
    # lets the user choose the splits file
    # doesn't load the file into memory
    boundslist = glob.glob('*.txt')
    boundslist.sort()

    if len(boundslist) == 0:
        print("No .txt file found!")
        raise SystemExit

    for i in range(len(boundslist)):
        print(str(i) + ' ' + boundslist[i])

    chosenfile = int(input("\n-> "))
    good = False
    while not good:
        try:
            boundsfilename = boundslist[int(chosenfile)]
            good = True
        except IndexError:
            print("Invalid value. Try again...")
            chosenfile = input("\n-> ")
        except ValueError:
            print("Value must be a number. Try again...")
            chosenfile = input("\n-> ")

    return boundsfilename


def select_in_file():
    # lets the user choose the .in file
    # doesn't load the file into memory
    inlist = glob.glob('*.in')
    inlist.sort()

    if len(inlist) == 0:
        print("No .in file found!")
        raise SystemExit

    for i in range(len(inlist)):
        print(str(i) + ' ' + inlist[i])

    chosenfile = input("\n-> ")
    good = False
    while not good:
        try:
            infilename = inlist[int(chosenfile)]
            good = True
        except IndexError:
            print("Invalid value. Try again...")
            chosenfile = input("\n-> ")
        except ValueError:
            print("Value must be a number. Try again...")
            chosenfile = input("\n-> ")

    return infilename


def fd3(name):
        os.system('./fd3 < {} > '.format(name) + name[:-3] + '.out')


def run_fd3(filenames):
    # runs all files supplied by filenames through fd3, in order

    if len(glob.glob("fd3")) == 0:
        print("\n### fd3 not found! ###")
        return

    print("\nFound {} .in files...\n".format(len(filenames)))

    pool = mp.Pool()

    # tic = time.time()
    bar = progressbar.ProgressBar(
        maxval=len(filenames),
        widgets=[
            progressbar.Bar('=', '[', ']'), ' ',
            progressbar.Percentage(), ' ',
            progressbar.ETA()])
    bar.start()
    for i, _ in enumerate(pool.imap(fd3, filenames), 1):
        bar.update(i)
    bar.finish()
    print("\nProcessed {0} files.".format(len(filenames)))


def average_overlap(filenames):
    # generates complete spectra with averaged overlaps
    # it is essential that the files are sorted by ascending wavelength
    # every loop uses the k'th index, starting at 1 in stead of 0

    w = np.array([])
    s1 = np.array([])
    s2 = np.array([])
    # print('\nReading light factors from .in file...')
    # infiles = glob.glob('*.in')
    # infiles.sort()
    # with open(infiles[0], 'r') as f:
    #     lines = f.readlines()
    #     linevals = lines[2].split(' ')
    #     lf1 = linevals[3]
    #     lf2 = linevals[4]

    bar = progressbar.ProgressBar(
        maxval=len(filenames),
        widgets=[
            progressbar.Bar('=', '[', ']'), ' ',
            progressbar.Percentage(), ' ',
            progressbar.ETA()])
    bar.start()
    # read the needed files
    file1 = np.loadtxt(filenames[0]).transpose()
    w1 = file1[0]
    s11 = file1[1] + (1 - np.mean(file1[1][0:20]))  # * lf1)
    s21 = file1[2] + (1 - np.mean(file1[2][0:20]))  # * lf2)
    for k in range(1, len(filenames)):
        file2 = np.loadtxt(filenames[k]).transpose()
        w2 = file2[0]
        s12 = file2[1] + (1 - np.mean(file2[1][0:20]))
        s22 = file2[2] + (1 - np.mean(file2[2][0:20]))

        # determine how many elements overlap
        n_overlap = len(np.intersect1d(w1, w2))
        w2 = w2[n_overlap:]

        # calculate averages over overlapping indices
        weights = np.array([np.arange(1, n_overlap + 1)[::-1],
                            np.arange(1, n_overlap + 1)])
        data = np.array([s11[-(n_overlap):], s12[:n_overlap]])
        newdata = np.average(data, axis=0, weights=weights)
        data2 = np.array([s21[-(n_overlap):], s22[:n_overlap]])
        newdata2 = np.average(data2, axis=0, weights=weights)

        # splicing in averaged overlap
        s11[-(n_overlap):] = newdata
        s12 = s12[n_overlap:]
        s21[-(n_overlap):] = newdata2
        s22 = s22[n_overlap:]

        w = np.append(w, w1)
        s1 = np.append(s1, s11)
        s2 = np.append(s2, s21)

        w1 = w2
        s11 = s12
        s21 = s22

        bar.update(k + 1)

    w = np.append(w, w1)
    s1 = np.append(s1, s11)
    s2 = np.append(s2, s21)

    bar.finish()

    np.savetxt('Sig_Aql_A_stitched.txt', np.array([np.exp(w), s1]).transpose())
    np.savetxt('Sig_Aql_B_stitched.txt', np.array([np.exp(w), s2]).transpose())


def clean():
    n = 0
    filenames = glob.glob('*used_[0-9]*')
    for name in filenames:
        os.remove(name)
    n += len(filenames)
    filenames = glob.glob('*[0-9].in')
    for name in filenames:
        os.remove(name)
    n += len(filenames)
    filenames = glob.glob('*[0-9].out')
    for name in filenames:
        os.remove(name)
    n += len(filenames)
    print("{} files cleaned up!".format(n))


def main():
    originalPath = os.getcwd()

    chd = input("Work in current directory? (Y/N): ")

    while chd not in ('Y', 'y', 'N', 'n'):
        chd = input("\nWork in current directory? (Y/N): ")
    if chd == 'N' or chd == 'n':
        originalPath = path_chooser()
        os.chdir(originalPath)

    edit = input("\nEdit split points? (Y/N): ")

    while edit not in ('Y', 'y', 'N', 'n'):
        edit = input("\nEdit split points? (Y/N): ")
    if edit == 'Y' or edit == 'y':
        picker(path_chooser())

    os.chdir(originalPath)

    print("\n### Select model .in file ###\n")

    infilename = select_in_file()

    print('\n### Select bounds file ###\n')

    boundsfilename = select_bounds_file()

    print("writing files...")
    setBounds(infilename, boundsfilename)
    print("Done")

    runchoice = input("\nRun fd3 "
                      "using the generated .in files? (Y/N): ")

    while runchoice not in ('Y', 'y', 'N', 'n'):
        runchoice = input("\nDo you want to run fd3 "
                          "using the generated .in files? (Y/N): ")

    if runchoice == 'Y' or runchoice == 'y':
        filenames = glob.glob("*[0-9].in")
        filenames.sort()
        run_fd3(filenames)

        print("\nStitching spectra...\n")
        modnames = glob.glob('*[0-9].obs.mod')
        modnames.sort()  # IMPORTANT
        average_overlap(modnames)
        print("Done!")

    cleanchoice = input('\nCleanup? (Y/N): ')
    while cleanchoice not in ('Y', 'y', 'N', 'n'):
        cleanchoice = input("\nCleanup? (Y/N): ")

    if cleanchoice == 'Y' or cleanchoice == 'y':
        clean()


print("""
### insplitter v1.2 ###
""")

main()