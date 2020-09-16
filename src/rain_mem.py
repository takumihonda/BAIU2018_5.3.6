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

JMA = False
#JMA = True



def main():

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 6, 28, 0, 0, 0 )
    stime = datetime( 2018, 6, 27, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    
    adt_h = 24
    adt = timedelta( hours=adt_h )
 
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 20, 300, 20)
    clevs = np.arange( 800, 1200, 4 )
    cmap = plt.cm.get_cmap("jet")

    extend = 'max'

    for m in range( 51 ):
        mem = str(m).zfill(4)    
        if m == 0:
           mem = "mean"
        
        rain = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m )
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
        
        #rain[ rain < np.min(levs) ] = np.nan
 
        if JMA:
           jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( vtime - adt , adt_h, ACUM=True )
           print( jma2d.shape, np.min(jma2d) )
           jma2d[jma2d < 0.1] = np.nan
           rain = jma2d

           lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )
           x2d, y2d = m_l[0](lon2d_jma, lat2d_jma) 

           draw_rec( m_l[0], ax1, slon, elon, slat, elat,
                     c='k', lw=3.0, ls='solid' )

           cmap.set_under('gray',alpha=1.0)
           extend = 'both'


        SHADE = ax1.contourf( x2d, y2d, rain, levels=levs, cmap=cmap,
                              extend=extend)
        

        pos = ax1.get_position()
        cb_width = 0.015
        cb_height = pos.height*0.98
        ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
        cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs)
        cb.ax.tick_params( labelsize=8 )
        

        if JMA:
           #x_l = [ x_ll, x_ur, x_ur, x_ll ]
           #y_l = [ y_ll, y_ll, y_ur, y_ur ]
 
           #ax1.plot( x_l, y_l, linewidth=10, color='k' )

           tit = 'JMA radar, valid: {0:}'.format( vtime.strftime('%HUTC %m/%d') )
           ofig = vtime.strftime('JMA_v%H%m%d') 
        else:
           CONT = ax1.contour( x2d, y2d, mslp*0.01, colors='k',
                               linewidths=0.5, levels=clevs )
           ax1.clabel( CONT, fontsize=7, fmt='%.0f' )
   
           tit = '{0:}, init: {1:}, valid: {2:}'.format( mem, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
           ofig = mem + vtime.strftime('_v%H%m%d') 
        fig.suptitle( tit, fontsize=12 )
        
    
        if not quick:
          opath = "png/rain_mem" + stime.strftime('_s%H%m%d')
          os.makedirs(opath, exist_ok=True)
    
          ofig = os.path.join(opath, ofig + ".png")
          plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
          print(ofig)
          plt.clf()
        else:
          print(ofig)
          plt.show()
    
        if JMA:
           sys.exit()


main()
