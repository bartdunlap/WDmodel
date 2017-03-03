#!/usr/bin/env python

from __future__ import print_function

import sys
from emcee.utils import MPIPool
from fit_WDmodel import get_options
from numpy import unique
import WDmodel
import WDmodel.fit
import WDmodel.viz
import WDmodel.io


def main(pool):
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)

    args = get_options(sys.argv[1:])

    specfile  = args.specfile
    outdir    = args.outdir
    rvmodel   = args.reddeningmodel
    ascale    = args.ascale
    nwalkers  = args.nwalkers
    nburnin   = args.nburnin
    nprod     = args.nprod
    discard   = args.discard
    everyn    = args.everyn
    redo      = args.redo
    balmer    = args.balmerlines
    ndraws    = args.ndraws
    savefig   = args.savefig
    excludepb = args.excludepb

    # set the object name and create output directories
    objname, outdir = WDmodel.io.set_objname_outdir_for_specfile(specfile, outdir=outdir)

    # restore data
    input_file = WDmodel.io.get_outfile(outdir, specfile, '_inputs.hdf5')
    res = WDmodel.io.read_fit_inputs(input_file)
    spec, cont_model, linedata, continuumdata, phot = res

    # restore params
    param_file = WDmodel.io.get_outfile(outdir, specfile, '_params.json')
    params = WDmodel.io.read_params(param_file)

    # init model
    model = WDmodel.WDmodel()

    # exclude passbands that we want excluded 
    if phot is not None:
        pbnames = unique(phot.pb) 
        if excludepb is not None:
            pbnames = list(set(pbnames) - set(excludepb))
    else:
        pbnames = []

    # get the throughput model 
    pbmodel = WDmodel.io.get_pbmodel(pbnames)

    result = WDmodel.fit.mpi_fit_model(spec, phot, model, pbmodel, params,\
                objname, outdir, specfile,\
                rvmodel=rvmodel,\
                ascale=ascale, nwalkers=nwalkers, nburnin=nburnin, nprod=nprod, everyn=everyn,\
                redo=redo, pool=pool)

    param_names, samples, samples_lnprob = result
    mcmc_params = WDmodel.io.copy_params(params)
    result = WDmodel.fit.get_fit_params_from_samples(param_names, samples, samples_lnprob, mcmc_params,\
                    nwalkers=nwalkers, nprod=nprod, discard=discard)
    mcmc_params, in_samp, in_lnprob = result
    outfile = WDmodel.io.get_outfile(outdir, specfile, '_result.json')
    WDmodel.io.write_params(mcmc_params, outfile)

    # plot the MCMC output
    WDmodel.viz.plot_mcmc_model(spec, phot, linedata,\
                objname, outdir, specfile,\
                model, cont_model,\
                mcmc_params, param_names, in_samp, in_lnprob,\
                rvmodel=rvmodel, balmer=balmer, ndraws=ndraws, savefig=savefig)

    return

if __name__ =='__main__':
    # Initialize the MPI-based pool used for parallelization.
    pool = MPIPool()

    main(pool)

    # Close the processes.
    pool.close()


