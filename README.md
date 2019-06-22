# fd3-helper
A toolkit to make working with fd3 easier. This tool was created for a bachelor project which required spectrum disentangling.

## fd3_helper
This tool helps to split a .in file into smaller pieces, allowing the user to set split points graphically. Runs fd3 over the split pieces and stitches the pieces together using a linearly weighted average. Requires the fd3 binary to be in the same folder. 

### Dependencies
+ Requires fd3 binary in the same directory
+ Requires python packages: `numpy`, `matplotlib`, `progressbar`, `multiprocessing`
  * Apart from `progressbar`, these are all included in the Anaconda environment. To install `progressbar`: `pip install progressbar`

## file2figure
Creates quick plots of common filetypes when using fd3: .mod, .txt, .fits.

### Dependencies
+ Python: `numpy`, `matplotlib`, `astropy`
  * These are all included with Anaconda.
