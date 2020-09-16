import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_var, def_cmap, draw_rec

from scipy.interpolate import griddata

quick = True   
#quick = False

TC = True
TC = False

def main( stime=datetime( 2018, 6, 30, 0), vtime_ref=datetime( 2018, 7, 6, 0 ),
          vtime=datetime( 2018, 7, 5, 0 ), nvar="RAIN", nvar2="MSLP", 
          hpa=950, hpa2=950 ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    

    adt_h = 24
    adt = timedelta( hours=adt_h )
    
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }


    lon2d, lat2d = get_lonlat( INFO, stime=stime )


    rain_l = np.zeros( 50 )

    # get reference
    for m in range( 50 ):
        #rain_ = get_arain( INFO, stime=stime, vtime=vtime_ref, adt=adt, m=m+1 )
        rain_ = get_var( INFO, nvar="RAIN", stime=stime, vtime=vtime_ref, m=m+1, adt=adt )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )


    print( rain_l )
    #print( np.sort( rain_l )[::-1] )
    #print( np.argsort( rain_l )[::-1] )

    mem_l = np.argsort( rain_l )[::-1]
    rain_l = np.sort( rain_l )[::-1]

    print( mem_l )
    print( rain_l )

    print( "" )

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16


    dth = 24
    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa )

    if nvar2 is not None:
       cmap2, levs2, unit2, extend2, nvar2_, fac2 = def_cmap( nvar=nvar2, hpa=hpa2 )


    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    lw = 0.5
    lc = 'k'
    if nvar == "PW":
       lc = 'gainsboro' #darkgray'
       lw = 1.0


    for i, m in enumerate( mem_l[::-1] ):
        rank = 50 - i 
        print( m )

        fig, ax1 = plt.subplots( 1, 1, figsize=( 5, 4.4 ) )
        fig.subplots_adjust( left=0.05, bottom=0.03, right=0.9, top=0.95,
                             wspace=0.1, hspace=0.3)
    
        m_l = prep_proj_multi('merc', [ ax1 ], ll_lon=lons, ur_lon=lone, 
                              ll_lat=lats, ur_lat=late, fs=6 )


        x2d, y2d = m_l[0](lon2d, lat2d)

        ptit = "Rank: {0:0=2}, mem: {1:0=2}".format( rank, m )
 
        var_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, 
                   adt=timedelta( hours=dth ), hpa=hpa )
        SHADE = ax1.contourf( x2d, y2d, var_*fac, 
                             cmap=cmap, levels=levs, extend=extend )

        var2_ = get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, 
                    adt=timedelta( hours=dth ), hpa=hpa2 )
        CONT = ax1.contour( x2d, y2d, var2_*fac2, colors=lc,
                            linewidths=lw, levels=levs2 )
      
        ax1.clabel( CONT, fontsize=6, fmt='%.0f' )

        draw_rec( m_l[0], ax1, slon, elon, slat, elat,
                  c='k', lw=1.0, ls='solid' )

        ax1.text( 0.5, 1.01, ptit,
                 fontsize=10, transform=ax1.transAxes,
                 horizontalalignment='center', 
                 verticalalignment='bottom',
                 zorder=5,
                 bbox = bbox )

        ptit2 = "Init:{0:}\nvalid:{1:}".format( stime.strftime('%HUTC %m/%d'), 
                 vtime.strftime('%HUTC %m/%d') )
        ax1.text( 0.99, 0.98, ptit2,
                 fontsize=10, transform=ax1.transAxes,
                 ha='right', 
                 va='top',
                 zorder=5,
                 bbox = bbox )

        pos = ax1.get_position()
        cb_width = 0.01
        cb_height = pos.height*0.9
        ax_cb = fig.add_axes( [pos.x1+0.005, pos.y1-cb_height, cb_width, cb_height] )
        cb = plt.colorbar( SHADE, cax=ax_cb, 
                           orientation = 'vertical', ticks=levs[::2] )
        cb.ax.tick_params( labelsize=7 )

        ax1.text( 0.95, 1.01, unit,
                 fontsize=9, transform=ax1.transAxes,
                 horizontalalignment='left', 
                 verticalalignment='bottom', )


        ofig = "1p_{0:}_{1:}_{2:}_{3:0=2}_{4:0=2}".format( nvar_, nvar2_, 
                   vtime.strftime('v%H%m%d'), rank, m )
        print( ofig )


        if not quick:
            opath = "png/1p_mem" + stime.strftime('_s%H%m%d')
            os.makedirs(opath, exist_ok=True)
          
            ofig = os.path.join(opath, ofig + ".png")
            plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
            print(ofig)
            plt.clf()
        else:
            print(ofig)
            plt.show()
    



stime = datetime( 2018, 6, 30, 0)
stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)
stime = datetime( 2018, 6, 28, 0)

vtime_ref = datetime( 2018, 7, 6, 0 )

vtime_l = [
           datetime( 2018, 7, 3, 0, 0 ),
           datetime( 2018, 7, 4, 0, 0 ),
           datetime( 2018, 7, 5, 0, 0 ),
           datetime( 2018, 7, 6, 0, 0 ),
          ]


nvar_l = [
          "PW", 
          "RAIN", 
          "THE", 
          "QV", 
          "QV", 
          "T", 
          "T", 
          ]

nvar2_l = [
          "MSLP", 
          "MSLP", 
          "Z", 
          "MSLP", 
          "Z", 
          "Z", 
          "Z", 
          ]

hpa_l = [ 950, 950, 950, 950, 500, 500, 300 ]


#nvar_l = [
#          #"RH",
#          "U",
#          "U",
#          #"QV",
#         ] 
#
#nvar2_l = [
#          "Z", 
#          "Z", 
#          #"MSLP", 
#          ]
#
##hpa_l = [ 850, 500, 300 ]
#hpa_l = [ 850, 850, ]
#hpa_l = [ 500, 500, ]
#hpa_l = [ 300, 300, ]

nvar_l = [
          "RAIN",
         ]

nvar2_l = [
          "MSLP", 
          ]

vtime_l = [
#           datetime( 2018, 7, 1, 0, 0 ),
#           datetime( 2018, 7, 2, 0, 0 ),
#           datetime( 2018, 7, 3, 0, 0 ),
#           datetime( 2018, 7, 4, 0, 0 ),
#           datetime( 2018, 7, 5, 0, 0 ),
           datetime( 2018, 7, 6, 0, 0 ),
          ]

for vtime in  vtime_l:
    for i, nvar in enumerate( nvar_l ):

        nvar2 = nvar2_l[i]
        hpa = hpa_l[i]
        hpa2 = hpa
    
        main( stime=stime, vtime_ref=vtime_ref, vtime=vtime, nvar=nvar, nvar2=nvar2, 
          hpa=hpa, hpa2=hpa2 )

