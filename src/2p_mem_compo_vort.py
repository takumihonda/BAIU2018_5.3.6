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


def main( stime=datetime( 2018, 6, 30, 0), vtime_ref=datetime( 2018, 7, 6, 0 ),
          vtime=datetime( 2018, 7, 5, 0 ), nvar="RAIN", nvar2="MSLP", 
          adt_h=24, cmem=10, dth2=0,
          hpa=950, hpa2=950 ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    

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

    print( "" )
    print( mem_l )
    print( rain_l )

    ptit_l = [ "Best {0:} - mean".format( cmem ),
               "Worst {0:} - mean".format( cmem ), ]
 
    pmem_l = [ 
               mem_l[0:cmem],  
               mem_l[-cmem:] 
             ]

    pnum_l = [ "(a)", "(b)", "(c)", "(d)" ] 

    fig, ( ax1,ax2 ) = plt.subplots( 1, 2, figsize=( 8, 3.5 ) )
    fig.subplots_adjust( left=0.05, bottom=0.05, right=0.9, top=0.9,
                         wspace=0.1, hspace=0.3)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    lons = 120
    lone = 151
    late = 42
    lats = 20


    #ax_l = [ ax1, ax2, ax3, ax4, ]# ax5, ax6 ]
    ax_l = [ ax1, ax2, ] # ax5, ax6 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=6 )

    x2d, y2d = m_l[0](lon2d, lat2d)

    dth_ = 0
    if nvar == "RAIN":
       dth_ = dth2
    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa, dth=dth_ )

    if nvar2 is not None:
       cmap2, levs2, unit2, extend2, nvar2_, fac2 = def_cmap( nvar=nvar2, hpa=hpa2 )

    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    lw = 0.5
    lc = 'k'
    if nvar == "PW":
       lc = 'gainsboro' #darkgray'
       lw = 1.0
#    lc = 'w'

    print( "get mean" )
    for m in range( len( mem_l ) ):
        print( m+1 )
        if m == 0:
           mvar_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
           mvar2_ = get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
        else:
           mvar_ += get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
           mvar2_ += get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )

    mvar_ = mvar_ / len( mem_l )
    mvar2_ = mvar2_ / len( mem_l )

    clevs = np.arange( -40, 45, 5 )
    clevs = np.arange( -20, 24, 4 )

    if nvar == "HDIV":
       clevs = np.arange( -5, 6, 1 )

    cmap = plt.cm.get_cmap("RdBu_r")
    extend = "both"

#    levs2 = np.arange( -20, -20, 40)
    #levs2 = [ -10, -5 ]
#    levs2 = [  -10, 10 ]
    fac2 = 1.0

    for i, ax in enumerate( ax_l ):
#       m = pmem_l[i]
       m = 0
       ptit = ptit_l[i]

       ax.text( 0.5, 0.98, ptit,
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='center', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )


       print( pmem_l[i], i )
       for j, m in enumerate( pmem_l[i] ):
           print( "mem", m, j )
           if j == 0:
              var_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
              var2_ = get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )
           else:
              var_ += get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
              var2_ += get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )

       var_ = var_ / cmem
       var2_ = var2_ / cmem
       SHADE = ax.contourf( x2d, y2d, ( var_ - mvar_ )*fac, 
                            cmap=cmap, levels=clevs, extend=extend )

       #CONT = ax.contour( x2d, y2d, ( var2_ - mvar2_ )*fac2, colors=lc,
       CONT = ax.contour( x2d, y2d,  mvar2_*fac2, colors=lc,
                          linewidths=lw, levels=levs2, linestyles="solid" )
      
#       ax.clabel( CONT, fontsize=6, fmt='%.0f' )
 

       draw_rec( m_l[0], ax, slon, elon, slat, elat,
                 c='k', lw=1.0, ls='solid' )
  

       if i == 1:
          pos = ax.get_position()
          cb_width = 0.01
          cb_height = pos.height*0.9
          ax_cb = fig.add_axes( [pos.x1+0.005, pos.y1-cb_height, cb_width, cb_height] )
          cb = plt.colorbar( SHADE, cax=ax_cb, 
                             orientation = 'vertical', ticks=clevs[::1] )
          cb.ax.tick_params( labelsize=7 )

          ax.text( 0.95, 1.01, unit,
                   fontsize=9, transform=ax.transAxes,
                   horizontalalignment='left', 
                   verticalalignment='bottom', )

       ax.text( 0.05, 0.98, pnum_l[i],
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='left', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )


 
    if nvar2 is not None:
       ofig = "2p_difm_{0:}_{1:}_{2:}_adt{3:0=3}".format( nvar_, nvar2_, vtime.strftime('v%m%d%H'), adt_h, )
       gtit = "{0:} & {1:}, init:{2:}, valid:{3:}".format( nvar_, nvar2_, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
    else:
       ofig = "4p_{0:}_{1:}_{2:0=3}".format( nvar_, vtime.strftime('v%H%m%d'), adt_h )
       gtit = "{0:}, init:{1:}, valid:{2:}".format( nvar_, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
   
    fig.suptitle( gtit, fontsize=12)

    if not quick:
       opath = "png/2p_cmem" + stime.strftime('_s%H%m%d_cmem') + str( cmem ).zfill(2)
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()



#####################

stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)
stime = datetime( 2018, 7, 3, 0)

vtime_l = [
#           datetime( 2018, 6, 30, 0, 0 ),
#           datetime( 2018, 7, 1, 0, 0 ),
#           datetime( 2018, 7, 2, 0, 0 ),
           datetime( 2018, 7, 3, 0, 0 ),
           datetime( 2018, 7, 3, 12, 0 ),
           datetime( 2018, 7, 4, 0, 0 ),
           datetime( 2018, 7, 4, 12, 0 ),
           datetime( 2018, 7, 5, 0, 0 ),
#           datetime( 2018, 7, 6, 0, 0 ),
#           datetime( 2018, 7, 7, 0, 0 ),
          ]




nvar_l = [
          #"OLR", 
          #"Q1_vg", 
          #"HDIV", 
          "VORT", 
          #"V", 
         ]

nvar2_l = [
          "Z", 
          #"Z", 
          ]
 
hpa_l = [  
          850, 
          #500, 
          #700, 
          #950, 
        ]

adt_h = 24
vtime_ref = datetime( 2018, 7, 6, 0 )

adt_h = 48
vtime_ref = datetime( 2018, 7, 7, 0 )

# only for RAIN
dth2 = 48

for vtime in  vtime_l:
    for i, nvar in enumerate( nvar_l ):

        nvar2 = nvar2_l[i]
        hpa = hpa_l[i]
        hpa2 = hpa
    
        main( stime=stime, vtime_ref=vtime_ref, vtime=vtime, nvar=nvar, nvar2=nvar2, 
              hpa=hpa, hpa2=hpa2, adt_h=adt_h, dth2=dth2)

