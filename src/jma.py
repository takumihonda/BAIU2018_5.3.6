import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_grads_JMA, draw_rec

quick = True   
quick = False




def main():

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 6, 28, 0, 0, 0 )
    stime = datetime( 2018, 6, 27, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    #vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    
    adt_h = 24
    adt = timedelta( hours=adt_h )
 
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 10, 155, 5 )
    clevs = np.arange( 800, 1200, 4 )
    cmap = plt.cm.get_cmap("jet")

    extend = 'max'

    fig, ((ax1)) = plt.subplots( 1, 1, figsize=(8, 6.0 ) )
    fig.subplots_adjust( left=0.07, bottom=0.05, right=0.94, top=0.95,
                         wspace=0.2, hspace=0.02)
        
    unit = "(mm/24h)"
    lons = 106
    lone = 164
    late = 49
    lats = 16
       
    ax_l = [ ax1 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, ll_lat=lats, ur_lat=late )
        
    x2d, y2d = m_l[0](lon2d, lat2d)

    jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( vtime - adt , adt_h, ACUM=True )
    print( jma2d.shape, np.min(jma2d) )
    jma2d[jma2d < 0.1] = np.nan
    rain = jma2d

    lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )
    x2d, y2d = m_l[0](lon2d_jma, lat2d_jma) 

    cmap.set_under('gray',alpha=1.0)
    extend = 'both'


    SHADE = ax1.contourf( x2d, y2d, rain, levels=levs, cmap=cmap,
                          extend=extend)

    pos = ax1.get_position()
    cb_width = 0.015
    cb_height = pos.height*0.8
    ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
    cb.ax.tick_params( labelsize=8, )
        
    tit = 'Previous 24-h accumulated JMA radar precipitation, valid: {0:}'.format( vtime.strftime('%HUTC %m/%d') )
    ofig = vtime.strftime('JMA_v%H%m%d') 


    #bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}
    ax1.text( 0.5, 1.05, tit,
              fontsize=14, transform=ax1.transAxes,
              horizontalalignment='center', 
              verticalalignment='center' )#,
              #bbox = bbox)

    ax1.text( 1.0001, 0.95, unit,
             fontsize=6, transform=ax1.transAxes,
             horizontalalignment='left', 
             verticalalignment='bottom', )

    draw_rec( m_l[0], ax1, slon, elon, slat, elat,
              c='k', lw=3.0, ls='solid' )


    if not quick:
       opath = "png/JMA_obs"
       os.makedirs(opath, exist_ok=True)
    
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()
    

    sys.exit()


 


        
    


main()
