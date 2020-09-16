import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_gph


quick = True   
quick = False


def main( stime=datetime( 2018, 6, 30, 0),
          vtime=datetime( 2018, 7, 5, 0 ) ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt = timedelta( hours=24 )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 10, 110, 10)
    clevs = np.arange( 0, 12000, 20 )
    cmap = plt.cm.get_cmap("hot_r")

    hpa = 500
    #hpa = 300
    hpa = 850


    gph_ = get_gph( INFO, stime=stime, vtime=vtime, m=0, hpa=hpa )


    mmax = 50
    egph = np.zeros( ( mmax, gph_.shape[0], gph_.shape[1] ) )


    for m in range( 0,mmax ):
        gph_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
        egph[m,:,:] = gph_
        if m % 5 == 0:
           print( m )
    evar = egph

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
        
    extend = 'max'

    print( np.max( np.std( evar, ddof=1, axis=0) ),
           np.min( np.std( evar, ddof=1, axis=0) ),
           np.max( np.mean( evar, axis=0) ),
           np.min( np.mean( evar, axis=0) ),
            )

    SHADE = ax1.contourf( x2d, y2d, np.std( evar, ddof=1, axis=0), 
                          levels=levs, cmap=cmap,
                          extend=extend )
           
   
    pos = ax1.get_position()
    cb_width = 0.015
    cb_height = pos.height*0.98
    ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs)
    cb.ax.tick_params( labelsize=8 )
           

    CONT = ax1.contour( x2d, y2d, np.mean( evar, axis=0 ), 
                        colors='k',
                        linewidths=0.5, levels=clevs )
    ax1.clabel( CONT, fontsize=7, fmt='%.0f' )

    tit = 'Z{0:}, spread & mean, init: {1:}, valid: {2:}'.format( str(hpa), stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )

    fig.suptitle( tit, fontsize=12 )
        
    ofig = "sprd" + vtime.strftime('_v%H%m%d') 
    
    if not quick:
      opath = "png/Z" + str(hpa) + "_sprd" + stime.strftime('_s%H%m%d')

      os.makedirs(opath, exist_ok=True)
    
      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
    else:
      print(ofig)
      plt.show()



stime = datetime( 2018, 6, 28, 0)
stime = datetime( 2018, 6, 27, 0)
#stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)

etime = datetime( 2018, 7, 6, 0 )
#stime = etime

stime = datetime( 2018, 6, 26, 0)
stime = datetime( 2018, 6, 27, 0)
stime = datetime( 2018, 6, 28, 0)
stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 6, 30, 0)
stime = datetime( 2018, 7, 1, 0)
stime = datetime( 2018, 7, 2, 0)

time = stime
while time <= etime:
   main( stime=stime, vtime=time )

   time += timedelta( days=1 )
