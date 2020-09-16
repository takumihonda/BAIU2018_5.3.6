import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp, get_prsvar, get_gph

quick = True   
quick = False



def main( vtime=datetime(2018, 7, 1, 0 ), hpa=500 ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt_h = 24
    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    clevs = np.arange( 800, 1200, 4 )

    mslp = get_mslp( INFO, stime=vtime, vtime=vtime, m=0 )
    gph = get_gph( INFO, stime=vtime, vtime=vtime, m=0 )
    var_ =  get_prsvar( INFO, nvar="Tprs", stime=vtime, vtime=vtime, m=0, hpa=hpa ) 

    print( np.nanmax(var_), np.nanmin(var_) )

    levs = np.arange( 270, 300, 1 )

    cmap = plt.cm.get_cmap("RdBu_r")
    levs = np.arange( 280, 301, 1 )
    levs = np.arange( 284, 297, 1 )


    if hpa < 300:
       levs = np.arange( 218, 231, 1 )
    elif hpa < 400:
       levs = np.arange( 238, 251, 1 )
    elif hpa < 600:
       levs = np.arange( 264, 275, 1 )
#    elif hpa > 900:
#       levs = np.arange( 0, 20, 1 )

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
        
    SHADE = ax1.contourf( x2d, y2d, var_,
                          cmap=cmap, extend='both',
                          levels=levs )

    pos = ax1.get_position()
    cb_width = 0.015
    cb_height = pos.height*0.98
    ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
    cb.ax.tick_params( labelsize=8 )
 
          
    clevs = np.arange( 0, 15000, 20 )
    CONT = ax1.contour( x2d, y2d, gph, colors='k',
                        linewidths=1.0, levels=clevs )
    ax1.clabel( CONT, fontsize=8, fmt='%.0f' )
#    CONT = ax1.contour( x2d, y2d, mslp*0.01, colors='k',#'gainsboro',
#                        linewidths=1.0, levels=clevs )
#    ax1.clabel( CONT, fontsize=8, fmt='%.0f' )
   
    tit = r'Analysis T{0:} (K), valid: {1:}'.format( hpa, vtime.strftime('%HUTC %m/%d') )
    ofig = "tk{0:}_v{1:}".format( hpa, vtime.strftime('%H%m%d') )
    fig.suptitle( tit, fontsize=12 )
        
    
    if not quick:
      opath = "png/TK_anal"
      os.makedirs(opath, exist_ok=True)
    
      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
    else:
      print(ofig)
      plt.show()
    

time = datetime( 2018, 6, 26, 0 )
etime = datetime( 2018, 7, 6, 0 )

hpa = 700
hpa = 500
hpa = 300
hpa = 200
#hpa = 950

while time <= etime:
    main( vtime=time, hpa=hpa )
    time += timedelta( days=1 )
