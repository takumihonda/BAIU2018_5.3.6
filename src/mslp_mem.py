import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, convolve_ave

quick = True   
quick = False

ng = 3
kernel = np.ones( (ng,ng)) / (ng**2)


def main():

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 6, 28, 0, 0, 0 )

    stime = datetime( 2018, 7, 2, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    vtime = datetime( 2018, 7, 3, 0, 0, 0 )
    vtime = datetime( 2018, 7, 1, 0, 0, 0 )
    vtime = datetime( 2018, 7, 4, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    
    adt_h = 24
    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 20, 300, 20)
    clevs = np.arange( 800, 1200, 4 )
    cmap = plt.cm.get_cmap("jet")

    for m in range( 51 ):
        mem = str(m).zfill(4)    
        if m == 0:
           mem = "mean"
        
        mslp = get_mslp( INFO, stime=stime, vtime=vtime, m=m )
        
        
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
 

        mslp_ = convolve_ave( mslp, kernel )
        cy, cx = np.unravel_index( np.argmin(mslp_), mslp_.shape ) 
 
        slp_x, slp_y = m_l[0]( lon2d[cy,cx], lat2d[cy,cx] )

        m_l[0].plot( slp_x, slp_y, marker='o', color='b',
                     markersize=10.0, label='Forecast' )

        if vtime == datetime( 2018, 7, 1, 0 ) or \
           vtime == datetime( 2018, 7, 2, 0 ) or \
           vtime == datetime( 2018, 7, 3, 0 ) or \
           vtime == datetime( 2018, 7, 4, 0 ):

           if vtime == datetime( 2018, 7, 1, 0 ):
              tlon = 127.7
              tlat = 23.6
           elif vtime == datetime( 2018, 7, 2, 0 ):
              tlon = 127.0
              tlat = 27.2
           elif vtime == datetime( 2018, 7, 3, 0 ):
              tlon = 128.2
              tlat = 32.0
           elif vtime == datetime( 2018, 7, 4, 0 ):
              tlon = 132.5
              tlat = 37.3

           slp_x, slp_y = m_l[0]( tlon, tlat )
           m_l[0].plot( slp_x, slp_y, marker='o', color='k',
                        markersize=10.0, label='Best Track' )

           ax1.legend( loc='lower right' )

        tit = '{0:}, init: {1:}, valid: {2:}'.format( mem, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
        ofig = mem + vtime.strftime('_v%H%m%d') 
        fig.suptitle( tit, fontsize=12 )
        
    
        if not quick:
          opath = "png/mslp_mem" + stime.strftime('_s%H%m%d')
          os.makedirs(opath, exist_ok=True)
    
          ofig = os.path.join(opath, ofig + ".png")
          plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
          print(ofig)
          plt.clf()
        else:
          print(ofig)
          plt.show()
    


main()
