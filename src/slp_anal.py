import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp

quick = True   
quick = False



def main():

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 6, 28, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    #vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    #vtime = datetime( 2018, 7, 5, 0, 0, 0 )
    vtime = datetime( 2018, 7, 4, 0, 0, 0 )
    
    adt_h = 24
    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 20, 300, 20)
    clevs = np.arange( 800, 1200, 4 )

    mslp = get_mslp( INFO, stime=vtime, vtime=vtime, m=0 )

        
    fig, ((ax1)) = plt.subplots( 1, 1, figsize=(8, 6.0 ) )
    fig.subplots_adjust( left=0.07, bottom=0.05, right=0.94, top=0.95,
                         wspace=0.2, hspace=0.02)
        
    lons = 105
    lone = 165
    late = 50
    lats = 15
        
    ax_l = [ ax1 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, ll_lat=lats, ur_lat=late )
        
    x2d, y2d = m_l[0](lon2d, lat2d)
        
 
    CONT = ax1.contour( x2d, y2d, mslp*0.01, colors='k',
                        linewidths=0.5, levels=clevs )
    ax1.clabel( CONT, fontsize=7, fmt='%.0f' )
   
    tit = 'Analysis ensemble mean MSLP (hPa), valid: {0:}'.format( vtime.strftime('%HUTC %m/%d') )
    ofig = vtime.strftime('mslp_v%H%m%d') 
    fig.suptitle( tit, fontsize=12 )
        
    
    if not quick:
      opath = "png/mslp_anal"
      os.makedirs(opath, exist_ok=True)
    
      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
    else:
      print(ofig)
      plt.show()
    


main()
