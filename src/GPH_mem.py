import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_gph

PLOT_SHADE = True
#PLOT_SHADE = False

quick = True   
#quick = False

FERR = True
#FERR = False

def main():

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    #stime = datetime( 2018, 6, 28, 0, 0, 0 )
    #stime = datetime( 2018, 7, 1, 0, 0, 0 )

    #vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    
    adt = timedelta( hours=24 )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    levs = np.arange( 20, 300, 20)
    clevs = np.arange( 0, 6000, 20 )
    cmap = plt.cm.get_cmap("jet")

    hpa = 500
    #hpa = 850

    if FERR:
       levs = np.arange( -100, 110, 10)
       cmap = plt.cm.get_cmap("RdBu_r")
       # Read analysis ensemble mean
       gph_a = get_gph( INFO, stime=vtime, vtime=vtime, m=0, hpa=hpa )

    for m in range( 51 ):
        mem = str(m).zfill(4)    
        if m == 0:
           mem = "mean"
        
        rain = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m )
        mslp = get_mslp( INFO, stime=stime, vtime=vtime, m=m )
        gph = get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )
#        print(gph.shape )
        
        
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
            
        # forecast variables
        var2d = rain    
        var2d_c = gph    

        extend = 'max'

        if FERR:
           var2d = gph - gph_a
           var2d_c = gph
           var2d_c = gph_a
           extend = 'both'


        if PLOT_SHADE:
           SHADE = ax1.contourf( x2d, y2d, var2d, levels=levs, cmap=cmap,
                                 extend=extend )
           
   
           pos = ax1.get_position()
           cb_width = 0.015
           cb_height = pos.height*0.98
           ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
           cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs)
           cb.ax.tick_params( labelsize=8 )
           

        CONT = ax1.contour( x2d, y2d, var2d_c, colors='k',
                            linewidths=0.5, levels=clevs )
        ax1.clabel( CONT, fontsize=7, fmt='%.0f' )

        tit = 'Z{0:}, {1:}, init: {2:}, valid: {3:}'.format( str(hpa), mem, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
        if FERR:
           tit = 'Forecast error Z{0:}, {1:}, init: {2:}, valid: {3:}'.format( str(hpa), mem, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )

        fig.suptitle( tit, fontsize=12 )
        
        ofig = mem + vtime.strftime('_v%H%m%d') 
    
        if not quick:
          opath = "png/Z" + str(hpa) + "_mem" + stime.strftime('_s%H%m%d')

          if FERR:
             opath += "_ferr"

          os.makedirs(opath, exist_ok=True)
    
          ofig = os.path.join(opath, ofig + ".png")
          plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
          print(ofig)
          plt.clf()
        else:
          print(ofig)
          plt.show()
    
    


main()
