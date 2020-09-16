import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
from tools_BAIU import get_lonlat, get_var, get_rain_idx, def_cmap, prep_proj_multi


quick = True   
#quick = False

if quick:
   res="c"
else:
   res="l"


ng = 3
kernel = np.ones( (ng,ng)) / (ng**2)


def main( 
          ctime=datetime( 2018, 7, 5, 0 ), 
          stime=datetime( 2018, 7, 5, 0 ), 
          vtime_ref=datetime( 2018, 7, 6, 0 ),
          dlon=1.0, nvar="MSLP", hpa=500 ):


    mmax = 50 # debug


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    rain_l, mem_l = get_rain_idx( INFO, slon=130.0, elon=137.5, 
                      slat=33.0, elat=36.0, vtime_ref=vtime_ref, stime=stime,
                      adt_h=24, mmax=50, )

    print( rain_l )
    print( mem_l )

    var2d_b = np.zeros( lon2d.shape ) 
    var2d_w = np.zeros( lon2d.shape ) 
    mmax = 10

    for i, mem in enumerate( mem_l[:mmax] ):
        print(i, mem )
        var2d_b += get_var( INFO, nvar=nvar, stime=stime, vtime=ctime, m=mem+1 )

    for i, mem in enumerate( mem_l[:-mmax-1:-1] ):
        print(i, mem )
        var2d_w += get_var( INFO, nvar=nvar, stime=stime, vtime=ctime, m=mem+1 )


    var2d_b = var2d_b / mmax
    var2d_w = var2d_w / mmax

    var2d_a = get_var( INFO, nvar=nvar, stime=ctime, vtime=ctime, m=0 )

    fig, ( (ax1,ax2), (ax3,ax4) ) = plt.subplots( 2, 2, figsize=( 8, 7 ) )
    fig.subplots_adjust( left=0.05, bottom=0.05, right=0.9, top=0.9,
                         wspace=0.1, hspace=0.3)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1,  ax2, ax3, ax4, ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone,
                          ll_lat=lats, ur_lat=late, fs=6 )

    x2d, y2d = m_l[0](lon2d, lat2d)

    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa )

    if nvar == "Z":
       levs = np.arange( 0, 10420, 20 )
       levs_diff = np.arange( -200, 220, 20 )
    elif nvar == "MSLP":
       levs = np.arange( 900, 1040, 4 )
       levs_diff = np.arange( -20, 22, 2 )
    elif nvar == "V":
       levs = np.arange( -20, 24, 4 )
       levs_diff = np.arange( -10, 11, 1 )
    cmap = plt.cm.get_cmap("RdBu_r")

    var_l = [ 
              var2d_b*fac, ( var2d_b-var2d_a )*fac,
              var2d_w*fac, ( var2d_w-var2d_a )*fac,
              ]
    levs_l = [ 
              levs, levs_diff,
              levs, levs_diff,
              ]

    for i, ax in enumerate( ax_l ):
       print( np.max( var_l[i]) )

       if i == 0 or i == 2:
          CONT = ax.contour( x2d, y2d, var_l[i],
                             levels=levs_l[i] )
       else:
          SHADE = ax.contourf( x2d, y2d, var_l[i],
                               levels=levs_l[i], cmap=cmap )

#       if i == 0:
#          pos = ax.get_position()
#          cb_width = 0.01
#          cb_height = pos.height*1.5
#          ax_cb = fig.add_axes( [pos.x1+0.005, pos.y1-cb_height, cb_width, cb_height] )
#          cb = plt.colorbar( SHADE, cax=ax_cb, 
#                             orientation = 'vertical', ticks=levs[::20] )
#          cb.ax.tick_params( labelsize=7 )

    plt.show()
    sys.exit()


    # Warm (better) => cool (worse)
    for m, mem in enumerate( mem_l[:] ):
        #print( mem, rain_l[m] )

        cc = cm.jet( (len(mem_l)-m-1) / len(mem_l) ), 
        ax1.quiver( 0.0, 0.0, stu_[mem], stv_[mem], 
                    color=cc, alpha=0.6, width=0.005,
                    angles='xy', scale_units='xy', scale=1 )

    print( stu_[0], stv_[0] )
    xmin = -15
    xmax = 15
    ymin = -15
    ymax = 15
    ax1.set_xlim( xmin, xmax )
    ax1.set_ylim( xmin, xmax )

    plt.show()
    sys.exit()








    ax1.legend( loc='lower right', )

    tit = "Initial {0:}".format( stime.strftime('%m/%d') )
    fig.suptitle( tit, fontsize=14 )


    opath = "png/track"
    ofig = "1p_track_s{0:}_dlon{1:}_ng{2:0=3}_{3:}".format( stime.strftime('%m%d'), dlon, ng, ctime.strftime('%m%d'),  ) 

    if not quick:

       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()



##################

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 5, 0 )

stime = datetime( 2018, 6, 30, 0 )
#stime = datetime( 2018, 6, 28, 0 )
#stime = datetime( 2018, 7, 2, 0 )
etime = stime

dlon = 1.0
dlon = 2.0
#dlon = 3.0

ctime = datetime( 2018, 6, 30, 0 )
ctime = datetime( 2018, 7, 6, 0 )
ctime = datetime( 2018, 7, 1, 0 )
#ctime = datetime( 2018, 7, 2, 0 )
#ctime = datetime( 2018, 7, 6, 0 )

vtime_ref = datetime( 2018, 7, 6, 0 )

nvar = "Z"
nvar = "MSLP"
nvar = "V"

stime = etime

time = stime
while time <= etime:
    main( 
          ctime=ctime,
          stime=time,
          dlon=dlon,
          vtime_ref=vtime_ref,
          nvar=nvar,
           )
    
    time += timedelta( days=1 )

