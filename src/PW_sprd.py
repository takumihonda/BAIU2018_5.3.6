import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_pw


quick = True   
#quick = False

MEAN = True
MEAN = False

def main( stime=datetime( 2018, 6, 30, 0),
          vtime=datetime( 2018, 7, 5, 0 ) ):


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt = timedelta( hours=24 )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    #levs = np.arange( 10, 110, 10)
    #clevs = np.arange( 0, 12000, 20 )
    levs = np.arange( 0, 17, 1)
    clevs = np.arange( 30, 80, 5 )
    clevs = np.arange( 900, 1100, 4 )
    cmap = plt.cm.get_cmap("hot_r")

    if MEAN:
       cmap = plt.cm.get_cmap("GnBu")
       cmap = plt.cm.get_cmap("Blues")
       #cmap.set_over('silver', alpha=1.0)
       levs = np.arange( 0, 62.5, 2.5)
       levs = np.arange( 0, 72.5, 2.5)

    pw_ = get_pw( INFO, stime=stime, vtime=vtime, m=0, )


    mmax = 50
    epw = np.zeros( ( mmax, pw_.shape[0], pw_.shape[1] ) )
    eslp = np.zeros( ( mmax, pw_.shape[0], pw_.shape[1] ) )


    for m in range( 0, mmax ):
        pw_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.001 # mm/m2
        slp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.01 # hPa
        epw[m,:,:] = pw_
        eslp[m,:,:] = slp_
        if m % 5 == 0:
           print( m )
    evar = epw

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

    var = np.std( evar, ddof=1, axis=0)
    skip = 1
    if MEAN:
       var = np.mean( evar, axis=0)
       skip = 2
    SHADE = ax1.contourf( x2d, y2d, var, 
                          levels=levs, cmap=cmap,
                          extend=extend )
           
   
    pos = ax1.get_position()
    cb_width = 0.015
    cb_height = pos.height*0.98
    ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::skip])
    cb.ax.tick_params( labelsize=8 )
        
   
    if MEAN:
       CONT0 = ax1.contour( x2d, y2d, var, 
                           colors='aqua', linestyles='solid',
                           linewidths=1.0, levels=[60,] ) #np.arange(60, 90, 2.5 ) )
       ax1.clabel( CONT0, fontsize=8, fmt='%.0f' )

 
    print( eslp.shape )
    slp_ = np.mean( eslp, axis=0 )
    if MEAN:
       lc = 'gainsboro'
    else:
       lc='k'
    CONT = ax1.contour( x2d, y2d, slp_, 
                        colors=lc,
                        linewidths=1.0, levels=clevs )
    ax1.clabel( CONT, fontsize=8, fmt='%.0f' )

    if MEAN:
       tit = 'Mean PW & MSLP, ' 
    else:
       tit = 'PW spread & MSLP, ' 
    tit += 'init: {0:}, valid: {1:}'.format( stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )

    fig.suptitle( tit, fontsize=12 )
        
    ofig = "sprd" + vtime.strftime('_v%H%m%d') 
    if MEAN: 
       ofig = "mean" + vtime.strftime('_v%H%m%d') 
   
    if not quick:
      opath = "png/PW_sprd" + stime.strftime('_s%H%m%d')

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
#stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 6, 29, 0)
#stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 7,  1, 0)
#stime = datetime( 2018, 7,  2, 0)
#stime = datetime( 2018, 7,  3, 0)

# forecast loop
time = stime
while time <= etime:
   main( stime=stime, vtime=time )

   time += timedelta( days=1 )


# analysis only
#etime = datetime( 2018, 7, 6, 0 )
#time = datetime( 2018, 6, 26, 0 )
#while time <= etime:
#   main( stime=time, vtime=time )
#
#   time += timedelta( days=1 )



