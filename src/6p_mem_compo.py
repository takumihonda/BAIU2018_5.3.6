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
quick = False

TC = True
TC = False

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

    ptit_l = [
               "Best {0:}".format( cmem ),
               "Worst {0:}".format( cmem ), 
               "Best {0:}".format( cmem ),
               "Worst {0:}".format( cmem ), 
               "Best {0:}".format( cmem ),
               "Worst {0:}".format( cmem ), 
             ]
 
    pmem_l = [ 
               mem_l[0:cmem],  
               mem_l[-cmem:], 
               mem_l[0:cmem],  
               mem_l[-cmem:], 
               mem_l[0:cmem],  
               mem_l[-cmem:], 
             ]

    pnum_l = [ "(a)", "(b)", "(c)", "(d)", "(e)", "(f)" ] 

    fig, ( ( ax1,ax2 ), (ax3,ax4), (ax5,ax6) ) = plt.subplots( 3, 2, figsize=( 7.0, 8.5 ) )
    fig.subplots_adjust( left=0.02, bottom=0.02, right=0.95, top=0.99,
                         wspace=0.0, hspace=0.1)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1, ax2, ax3, ax4, ax5, ax6 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=6 )

    x2d, y2d = m_l[0](lon2d, lat2d)


    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    lw = 0.5
    lc = 'k'
    if nvar == "PW":
       lc = 'gainsboro' #darkgray'
       lw = 1.0
#    lc = 'w'

    vtime_l = [
               datetime( 2018, 7, 7, 0 ), 
               datetime( 2018, 7, 7, 0 ), 
               datetime( 2018, 7, 3, 0 ), 
               datetime( 2018, 7, 3, 0 ), 
               datetime( 2018, 7, 5, 0 ), 
               datetime( 2018, 7, 5, 0 ), 
              ]


    nvar1_l = [ 
               "RAIN", "RAIN", 
               "OLR", "OLR",
               "V", "V"
               ]

    nvar2_l = [ 
               "MSLP", "MSLP", 
               "MSLP", "MSLP", 
               "Z", "Z", 
              ]

    for i, ax in enumerate( ax_l ):
#       m = pmem_l[i]
       m = 0
       ptit = ptit_l[i] 


       nvar = nvar1_l[i]
       nvar2 = nvar2_l[i]
       vtime = vtime_l[i]

       dth_ = 0
       if nvar == "RAIN":
          dth_ = dth2
       cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa, dth=dth_ )


       if nvar2 is not None:
          cmap2, levs2, unit2, extend2, nvar2_, fac2 = def_cmap( nvar=nvar2, hpa=hpa2 )


       ax.text( 0.5, 0.98, ptit + "\n" + nvar_,
                fontsize=9, transform=ax.transAxes,
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
       SHADE = ax.contourf( x2d, y2d, var_*fac, 
                            cmap=cmap, levels=levs, extend=extend )

       CONT = ax.contour( x2d, y2d, var2_*fac2, colors=lc,
                          linewidths=lw, levels=levs2 )
      
       ax.clabel( CONT, fontsize=6, fmt='%.0f' )
 

       draw_rec( m_l[0], ax, slon, elon, slat, elat,
                 c='k', lw=1.0, ls='solid' )
  

       if i == 1 or i == 3 or i == 5: 
          skip = 2
          if i ==3: 
             skip = 4
          pos = ax.get_position()
          cb_width = 0.01
          cb_height = pos.height*0.9
          ax_cb = fig.add_axes( [pos.x1+0.005, pos.y0, cb_width, cb_height] )
          cb = plt.colorbar( SHADE, cax=ax_cb, 
                             orientation = 'vertical', ticks=levs[::skip] )
          cb.ax.tick_params( labelsize=7 )

          ax.text( 1.01, 1.0, unit,
                   fontsize=8, transform=ax.transAxes,
                   ha='left', 
                   va='top', )

       ax.text( 0.05, 0.98, pnum_l[i],
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='left', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )


 
    ofig = "6p_RAIN_OLR_V"

    if not quick:
       opath = "png/6p_cmem" + stime.strftime('_s%H%m%d_cmem') + str( cmem ).zfill(2)
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
          "PW", 
          "RAIN", 
          "THE", 
          "QV", 
          "QV", 
          "T", 
          "T", 
          "U", 
          "U", 
          "U", 
          "V", 
          "V", 
          "V", 
          ]

nvar2_l = [
          "MSLP", 
          "MSLP", 
          "Z", 
          "MSLP", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          "Z", 
          ]

hpa_l = [ 950, 950, 950, 950, 500, 500, 300, 850, 500, 300, 850, 500, 300 ]


nvar_l = [
          "OLR", 
          #"Q1_vg", 
          #"VORT", 
          #"RAIN", 
          #"HDIV", 
         ]

nvar2_l = [
          "MSLP", 
          #"Z", 
          ]
 
hpa_l = [  
          850, 
          #950, 
          #500, 
        ]

adt_h = 24
vtime_ref = datetime( 2018, 7, 6, 0 )

adt_h = 48
vtime_ref = datetime( 2018, 7, 7, 0 )

# only for RAIN
dth2 = 48

cmem = 10

for vtime in  vtime_l:
    for i, nvar in enumerate( nvar_l ):

        nvar2 = nvar2_l[i]
        hpa = hpa_l[i]
        hpa2 = hpa
    
        main( stime=stime, vtime_ref=vtime_ref, vtime=vtime, nvar=nvar, nvar2=nvar2, 
              hpa=hpa, hpa2=hpa2, adt_h=adt_h, dth2=dth2, cmem=cmem )

