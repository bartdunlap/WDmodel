from pathlib import Path
import sys
import argparse
import warnings
import numpy as np
from scipy.interpolate import Akima1DInterpolator
import h5py
import time


def getKoesterGrid(VOTdir='.', lggl=None, lggh=None, Tl=None, Th=None,
                   wvl=None, wvh=None, dwv=0.01):
    """
    Generate grid of white dwarf spectra from D. Koester models.
    ASCII files available from the Spanish Virtual Observatory (SVO) at
    http://svo2.cab.inta-csic.es/theory/newov2/index.php?models=koester2
    Interpolate spectra to regular wavelength grid with spacing ``dwv`` and
    return grid of spectral flux with specified log g, Teff, and wavelength
    bounds.

    Parameters 
    ----------
    VOTdir : str
        Directory containing ascii files of Koester white dwarf spectra from
        the SVO.
    lggl : float
        Lower bound on log g for output grid.  If not specified, use min log g
        found in input files.
    lggh : float
        Upper bound on log g for output grid.  If not specified, use max log g
        found in input files
    Tl : float
        Lower bound on Teff for output grid.  If not specified, use min Teff
        found in input files.
    Th : float
        Upper bound on Teff for output grid.  If not specified, use max Teff
        found in input files.
    wvl : float
        Lower bound on wavelength for output grid (in Angstrom).  If not
        specified, use 899.23 Ang.
    wvh : float
        Upper bound on wavelength for output grid (in Angstrom).  If not
        specified, use 29991.8 Ang.
    dwv : float
        Wavelength spacing for interpolated output (in Angstrom)
    
    Returns
    -------
    wint : ndarray
        Output wavelength array (in Angstroms) from ``wvl`` to ``wvh`` with
        regular spacing ``dwv``.
    gv_m : ndarray
        Output vector of unique log g values in ascending order
    tv_m : ndarray
        Output vector of unique Teff values in ascending order
    specrs_m : ndarray
        Output array of fluxes interpolated to regular wavelength interval
        using :py:class:`scipy.interpolate.Akima1DInterpolator`
        Shape is (len(``int``), len(``gv_m``), len(``tv_m``)).
    filesize : float
        Crude estimate of the output file size in MB.

    Raises
    ------
    IOError
        If the input directory or files do not exist.
    ValueError
        If any input bounds are outside the grid values
    
    Notes
    -----
    The VOtable output generated by the SVO does not conform to the standard,
    so astropy won't parse it.  Therefore, this just uses the ascii option.
    Some of the spectra have duplicate wavelength values.  This uses
    :py:func:`numpy.unique` to remove duplicates.
    """

    p = Path(VOTdir)

    if not p.exists():
        message = 'Directory {} does not exist'.format(VOTdir)
        raise IOError(message)

    nspec = len(list(p.glob('*dk.dat.txt')))
    if nspec == 0:
        message = 'No files of format *dk.dat.txt in {}'.format(VOTdir)
        raise IOError(message)

    if wvl is None:
        wvl = 899.23
        print('Setting min wavelength to {:f.2} Ang'.format(wvl))
    if wvh is None:
        wvh = 29991.8
        print('Setting max wavelength to {:f.2} Ang'.format(wvh))

    tvec = np.zeros(nspec)
    gvec = np.zeros(nspec)
    wint = np.arange(wvl, wvh, dwv)
    nw = len(wint)
    spec = np.zeros((nw, nspec))

    print('Reading in and interpolating spectra.  This may take a minute.')
    for i, f in enumerate(p.glob('*dk.dat.txt')):
        tvec[i] = np.asfarray(f.name[2:7])
        gvec[i] = np.asfarray(f.name[8:11])/100.
        wv0, flx0 = np.loadtxt(f, unpack=True)

        wv, uid = np.unique(wv0, return_index=True)
        flx = flx0[uid]

        if wvl < np.min(wv):
            message = ('Minimum wavelength in model is greater than requested '
                       'minimum.')
            raise ValueError(message)

        if wvh > np.max(wv):
            message = ('Maximum wavelength in model is less than requested '
                       'maximum.')
            raise ValueError(message)

        sp_wvfl = Akima1DInterpolator(wv, flx)
        spec[:, i] = sp_wvfl(wint)

        # if (tvec[i] == 15000.) & (gvec[i] == 8.75):
        #     print(tvec[i], gvec[i])
        #     plt.plot(wv, flx, '.')
        #     plt.plot(wint, sp_wvfl(wint))
        #     plt.show()

    gmin = np.min(gvec)
    gmax = np.max(gvec)
    tmin = np.min(tvec)
    tmax = np.max(tvec)

    # Warn if requested bounds are broader than grid
    if gmin > lggl:
        message = ('Minimum log g in input file grid is {:g}, which is greater '
                    'than the desired minimum, {:g}.  '
                    'Using {:g}'.format(gmin, lggl, gmin))
        warnings.warn(message)

    if gmax < lggh:
        message = ('Maximum log g in input file grid is {:g}, which is less '
                    'than the desired maximum, {:g}.  '
                    'Using {:g}'.format(gmax, lggh, gmax))
        warnings.warn(message)

    if tmin > Tl:
        message = ('Minimum log g in input file grid is {:g}, which is greater '
                    'than the desired minimum, {:g}.  '
                    'Using {:g}'.format(tmin, Tl, tmin))
        warnings.warn(message)

    if tmax < Th:
        message = ('Maximum log g in input file grid is {:g}, which is less '
                    'than the desired maximum, {:g}.  '
                    'Using {:g}'.format(tmax, Th, tmax))
        warnings.warn(message)

    ind = np.lexsort((tvec, gvec))

    t12 = time.perf_counter()
    specsrt = spec[:, ind]
    gvsrt = gvec[ind]
    tvsrt = tvec[ind]
    t13 = time.perf_counter()
    print('time to reindex', t13-t12)

    if lggl is None:
        lggl = gmin
    if lggh is None:
        lggh = gmax
    if Tl is None:
        Tl = tmin
    if Th is None:
        Th = tmax

    ep = .0001
    gcond = (gvsrt >= (lggl - ep)) & (gvsrt <= (lggh + ep))
    ep = 1.
    tcond = (tvsrt >= (Tl - ep)) & (tvsrt <= (Th + ep))

    if not any(gcond):
        message = ('No log g values in input file grid are within the desired ' 
                   'output range.')
        raise ValueError(message)

    if not any(tcond):
        message = ('No Teff values in input file grid are within the desired ' 
                   'output range.')
        raise ValueError(message)
    
    gtmask = np.array(gcond & tcond)

    spec_m = specsrt[:, gtmask]

    gv = np.unique(gvsrt[gtmask])
    tv = np.unique(tvsrt[gtmask])
    ng = len(gv)
    nt = len(tv)

    specrs = spec_m.reshape((nw, ng, nt))
    print(specrs.shape)
    print(spec_m.shape)

    # indg = np.squeeze(np.where(gv == 8.75))
    # indt = np.squeeze(np.where(tv == 15000.))
    # sp = specrs[:, indg, indt]
    # plt.plot(wint, sp)
    # plt.show()

    filesize = specrs.nbytes + wint.nbytes + tv.nbytes + gv.nbytes
    filesize = filesize/(1024.*1024.)
    print('Output grid file will be approx. {:g} MB'.format(filesize))
    print('and contain {:g} spectra at {:g} log g points and {:g} Teff '
          'points.'.format(spec_m.shape[1], ng, nt))

    return wint, gv, tv, specrs, filesize
    

def writehdf(wv, gvec, tvec, flux, filename='KoesterGrids.hdf5',
             grid_name='default', writehead=False):
    """
    Writes spectral grid to hdf5 file in format suitable to be read by
    :py:func:`WDmodel.io.read_model_grid`. Prompts user if file already exists.

    Parameters
    ----------
    wv : array-like
        Wavelength array (in Angstroms).
    gvec : array-like
        Vector of log g values in ascending order
    tvec : array-like
        Vector of Teff values in ascending order
    flux : array-like
        Array of fluxes with shape (len(``wv``), len(``gvec``), len(``tvec``)).
    filename : str
        Name of output hdf5 file.
    grid_name : str
        Name of output group containing grid.
    writehead : bool
        If ``True``, include hardwired header info in hdf5 attributes.
    
    Notes
    -----
    Header infomration, including units are hardwired and specific to the
    Koester WD models currently at SVO.
    """

    if Path(filename).is_file():
        message = '{} already exists.  Do you want to overwrite? (y/n) '.format(filename)
        if input(message).lower() != 'y':
            message = 'Input new filename: '
            filename = input(message)

    hf = h5py.File(filename, 'w')
    g = hf.create_group(grid_name)

    # in Angstroms, equally spaced
    g.create_dataset('wave', data=wv)

    g.create_dataset('ggrid', data=gvec)
    g.create_dataset('tgrid', data=tvec)

    # flux is Nwave x Nggrid x Ntgrid
    g.create_dataset('flux', data=flux)

    if writehead:
        info = ('Model white dwarf spectra of D. Koester from Spanish Virtual '
                'Observatory '
                'http://svo2.cab.inta-csic.es/theory/newov2/index.php?models=koester2 '
                'spline interpolated onto regular wavelength grid. Fromatted '
                'for use with WDmodel python package.')
        g.attrs['info'] = info
        g['wave'].attrs['unit'] = 'Angstrom'
        g['ggrid'].attrs['unit'] = 'log [cm/s^2]'
        g['tgrid'].attrs['unit'] = 'Kelvin'
        g['flux'].attrs['unit'] = 'erg/cm^2/s/A'


def main(inargs=None):
    """
    Get command line options and pass to :py:func:`makeKoesterGrid`, which
    returns spectral grid on regular wavelength interval.
    Passes wavelength, logg, Teff, and flux arrays to :py:func:`writehdf` to
    write out grid if ``write`` is ``True``.
    Prompts to confirm write if file size is > ~500 MB.

    Parameters
    ----------
    inargs : array-like
        list of the input command line arguments
    """

    if inargs is None:
        inargs = sys.argv[1:]

    parser = argparse.ArgumentParser()

    parser.add_argument('--lggl',  required=False, type=float, default=7.25,
                        help="log g lower bound for output grid")
    parser.add_argument('--lggh',  required=False, type=float, default=9.5,
                        help="log g upper bound for output grid")
    parser.add_argument('--Tl',  required=False, type=float, default=5000.,
                        help="Teff lower bound for output grid")
    parser.add_argument('--Th',  required=False, type=float, default=80000.,
                        help="Teff upper bound for output grid")
    parser.add_argument('--dir',  required=False, type=str,
                        default='makegrid/models_123456789/koester2',
                        help="directory containing *.dk.dat.txt files with "
                        "Koester spectra")
    parser.add_argument('--wvl',  required=False, type=float, default=3200.,
                        help="Lower bound for output grid wavelength "
                        "(in Angstroms)")
    parser.add_argument('--wvh',  required=False, type=float, default=10500.,
                        help="Upper bound for output grid wavelength "
                        "(in Angstroms)")
    parser.add_argument('--dwv',  required=False, type=float, default=0.01,
                        help="Wavelength spacing (in Angstroms) for "
                        "output grid")
    parser.add_argument('--outfile',  required=False, type=str,
                        default='KoesterGrids.hdf5',
                        help="output filename for hdf5 file containing grid")
    parser.add_argument('--outgroup',  required=False, type=str,
                        default='default',
                        help="output group name in hdf5 file to contain grid")
    parser.add_argument('--write',  required=False, action='store_true',
                        help="Write out hdf5 file.")
    parser.add_argument('--header',  required=False, action='store_true',
                        help="Include attribute info in hdf5 file.")

    args = parser.parse_args()

    lggl = args.lggl
    lggh = args.lggh
    Tl = args.Tl
    Th = args.Th
    VOTdir = args.dir
    wvl = args.wvl
    wvh = args.wvh
    dwv = args.dwv
    filename= args.outfile
    grid_name = args.outgroup
    write = args.write
    header = args.header

    wint, gv_m, tv_m, specrs_m, fsz = getKoesterGrid(VOTdir=VOTdir, lggl=lggl,
                                                     lggh=lggh, Tl=Tl, Th=Th,
                                                     wvl=wvl, wvh=wvh, dwv=dwv)

    if write & (fsz > 500.):
        message = 'Would you like to proceed with writing file to disk? (y/n) '
        if input(message).lower() != 'y':
            write = False

    if write:
        writehdf(wint, gv_m, tv_m, specrs_m, filename=filename,
                 grid_name=grid_name, writehead=header)


if __name__=='__main__':
    inargs = sys.argv[1:]
    main(inargs)

