#!/usr/bin/env python
"""
Run MSISE00, save to NetCDF4 (HDF5) and/or plot.

Example:
Poker Flat Research Range altitude profile:

PlotMSIS.py 2018-01-01 -c 65 -148

"""
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import msise00
from argparse import ArgumentParser
from gridaurora.worldgrid import latlonworldgrid
try:
    from matplotlib.pyplot import show
    import msise00.plots as msplots
    import seaborn as sns
    sns.set_style('ticks')
except ImportError as e:
    print(e)
    msplots = None  # type: ignore


def main():
    p = ArgumentParser(description='calls MSISE-00 from Python, save to NetCDF4 and/or plot')
    p.add_argument('-t', '--time',
                   help='time: (single time or START STOP (1 hour time step) or list of times)',
                   nargs='+', default=[str(datetime.now()-timedelta(days=180))])
    p.add_argument('-a', '--altkm', help='altitude (km). scalar, or (start,stop,step) or list of alts.',
                   type=float, nargs='+', default=[200.])
    p.add_argument('-c', '--latlon', help='geodetic latitude/longitude (deg)',
                   metavar=('lat', 'lon'),
                   type=float, nargs=2)
    p.add_argument('-o', '--odir', help='directory to write plots to')
    p.add_argument('-w', help='NetCDF4 .nc filename to write')
    p.add_argument('-gs', help='geographic grid spacing (lat, lon)',
                   nargs=2, type=float, default=(10, 10))
    p.add_argument('-q', '--quiet', help='disable plotting', action='store_true')
    P = p.parse_args()

# %% altitude
    if len(P.altkm) == 1:
        altkm = np.atleast_1d(P.altkm[0])
    elif len(P.altkm) == 3:
        altkm = np.arange(*P.altkm)
    else:
        altkm = np.asarray(P.altkm)

    print(f'using altitudes from {altkm[0]:.1f} to {altkm[-1]:.1f} km')
# %% latlon
    if P.latlon is not None:
        glat, glon = P.latlon
    else:
        print(f'auto whole-world grid mode at {altkm[0]} km altitude')
        glat, glon = latlonworldgrid(*P.gs)
# %% run
    atmos = msise00.run(P.time, altkm, glat, glon)
# %% save
    if P.w:
        ncfn = Path(P.w).expanduser()
        print('saving', ncfn)
        atmos.to_netcdf(ncfn)
# %% plot
    if msplots is not None and not P.quiet:
        msplots.plotgtd(atmos, P.odir)
        show()
    else:
        print('skipped plots')


if __name__ == '__main__':
    main()
