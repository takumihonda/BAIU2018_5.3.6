import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp, get_gph, draw_prapiroon, get_prsvar, get_pw

from scipy.interpolate import griddata

quick = True   
quick = False

TC = True

def main( stime=datetime( 2018, 6, 30, 0), 
          vtime=datetime( 2018, 7, 5, 0 ) ):

    nvar = "MSLP"
    nvar = "Z"
    nvar = "Vprs"
    nvar = "PW"

    hpa = 500
    #hpa = 300

    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    

    vtime_ref = datetime( 2018, 7, 6, 0, 0, 0 )

    adt_h = 24
    adt = timedelta( hours=adt_h )
    
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }



    opath = "dat/ts_s" + stime.strftime('%H%m%d')
    os.makedirs(opath, exist_ok=True)

    of = 'v{0:}_thrs{1:03}mm_lon{2:04}_{3:04}_lat{4:04}_{5:04}.npz'.format( vtime_ref.strftime('%H%m%d'), thrs , slon, elon, slat, elat )
    print( of )

    data = np.load( os.path.join( opath, of) )

    ts_l = data['ts']   
    mem_l = data['mem']   

    print( ts_l, mem_l )

    lon2d, lat2d = get_lonlat( INFO, stime=stime )


    if nvar == "MSLP":
       clevs = np.arange( 800, 1200, 4 )
       fac = 0.01
       unit = "(hPa)"
       dif_clevs = np.arange( -10, 12, 2 )
    elif nvar == "Z":
       clevs = np.arange( 0, 12000, 20 )
       fac = 1.0
       unit = "(m)"
       dif_clevs = np.arange( -50, 55, 5 )
    elif nvar == "PW":
       clevs = np.arange( 20, 70, 2.5 )
       fac = 0.001
       unit = r'(mm$^{-2}$)'
       dif_clevs = np.arange( -10, 11, 1 )
    elif nvar == "Vprs" or nvar == "Uprs":
       clevs = np.arange( -36, 40, 4 )
       fac = 1.0
       unit = r'(ms$^{-1}$)'
       dif_clevs = np.arange( -10, 12, 1 )
    

    # better member
    var_b = np.zeros( lon2d.shape )
    blon_l = []
    blat_l = []
    bmslp_l = []

    # worse member
    var_w = np.zeros( lon2d.shape )
    wlon_l = []
    wlat_l = []
    wmslp_l = []

    clevs_l = [ clevs, clevs, dif_clevs ]
    cmap = plt.cm.get_cmap("GnBu")
    cmap_dif = plt.cm.get_cmap("BrBG")

    cmap_l = [ cmap, cmap, cmap_dif ] 

    mem_max = 20
    for m in mem_l[0:mem_max]:
        print( "better ", m+1 )
        #var_b_ = get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )
        if nvar == "MSLP":
           var_b += get_mslp( INFO, stime=stime, vtime=vtime, m=m+1 )
        elif nvar == "Z":
           var_b += get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
        elif nvar == "PW":
           var_b += get_pw( INFO, stime=stime, vtime=vtime, m=m+1 )
        else:
           var_b += get_prsvar( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, hpa=hpa )

        mslp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1 )
        cy, cx = np.unravel_index( np.argmin(mslp_), mslp_.shape ) 
        blon_l.append( lon2d[cy,cx] )
        blat_l.append( lat2d[cy,cx] )
        bmslp_l.append( mslp_[cy,cx] )

    #print(mem_l[len(mem_l)-mem_max:len(mem_l):1])
    print("")
    for m in mem_l[len(mem_l)-mem_max:len(mem_l):1]:
        print( "worse ",m )
        if nvar == "MSLP":
           var_w += get_mslp( INFO, stime=stime, vtime=vtime, m=m+1 )
        elif nvar == "Z":
           var_w += get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
        elif nvar == "PW":
           var_w += get_pw( INFO, stime=stime, vtime=vtime, m=m+1 )
        else:
           var_w += get_prsvar( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, hpa=hpa )

        mslp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1 )
        cy, cx = np.unravel_index( np.argmin(mslp_), mslp_.shape ) 
        wlon_l.append( lon2d[cy,cx] )
        wlat_l.append( lat2d[cy,cx] )
        wmslp_l.append( mslp_[cy,cx] )

    var_b = var_b / mem_max
    var_w = var_w / mem_max


    fig, ( (ax1,ax2,ax3) ) = plt.subplots( 1, 3, figsize=( 10.5, 3.8 ) )
    fig.subplots_adjust( left=0.04, bottom=0.01, right=0.96, top=0.95,
                         wspace=0.1, hspace=0.02)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1, ax2, ax3 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=5 )


    x2d, y2d = m_l[0](lon2d, lat2d)
 
    tit_l = [ "Better {0:} members".format( mem_max ), 
              "Worse {0:} members".format( mem_max ), 
              "DIF" ]
    var_l = [ var_b*fac, var_w*fac, (var_b-var_w)*fac ]

    bbox = {'facecolor':'w', 'alpha':0.9, 'pad':2}

    tclon_l = [ blon_l, wlon_l ]
    tclat_l = [ blat_l, wlat_l ]
    tcmslp_l = [ bmslp_l, wmslp_l ]

    for i, ax in enumerate( ax_l ):

        print( "CHK", i, np.max( var_l[i] ), np.min( var_l[i] ) )

        SHADE = ax.contourf( x2d, y2d, var_l[i], 
                             cmap=cmap_l[i], levels=clevs_l[i], extend='both' )
      
        pos = ax.get_position()
        cb_width = 0.005
        cb_height = pos.height*0.98
        ax_cb = fig.add_axes( [pos.x1+0.001, pos.y0+0.01, cb_width, cb_height] )
        cb = plt.colorbar( SHADE, cax=ax_cb, 
                           orientation = 'vertical', ) #ticks=levs)
        cb.ax.tick_params( labelsize=6 )

#           CONT = ax.contour( x2d, y2d, var_l[i], colors='k',
#                              linewidths=0.5, levels=clevs )
#      
#           ax.clabel( CONT, fontsize=7, fmt='%.0f' )
# 
#           if TC:
#
#              _, _, _ = draw_prapiroon( m_l[i], ax, time=vtime, 
#                                c='b', ms=25.0, marker='x' )
#
#              tcxs, tcys = m_l[i]( tclon_l[i], tclat_l[i])
#              m_l[i].plot( tcxs, tcys, marker='o', color='r',
#                           markersize=3.0, linestyle='None' )
#
#
#              print( "TC intensity:{0:.1f}hPa".format( np.mean( tcmslp_l[i] )*0.01 ) )
#
#              ax.text( 0.5, 0.05, "MSLP: {0:.1f}hPa".format( np.mean( tcmslp_l[i] )*0.01 ),
#                       fontsize=9, transform=ax.transAxes,
#                       horizontalalignment='center', 
#                       verticalalignment='center',
#                       bbox = bbox)

        ax.set_title( tit_l[i], size=12, loc = 'center' )
       

    if nvar == "Z":
       nvar += str( hpa )

    gtit = "Composite {0:} {1:}, init:{2:}, valid:{3:}".format( nvar, unit, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
    fig.suptitle( gtit, fontsize=14)


    ofig = "3p_" + nvar + vtime.strftime('_v%H%m%d') 
    print( ofig )

    if not quick:
       opath = "png/comp_mem" + stime.strftime('_s%H%m%d')
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()





stime = datetime( 2018, 6, 28, 0)
stime = datetime( 2018, 6, 29, 0)
#stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 26, 0)
#stime = datetime( 2018, 6, 27, 0)
#stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)

etime = datetime( 2018, 7, 6, 0 )

time = stime
while time <= etime:
   main( stime=stime, vtime=time )

   time += timedelta( days=1 )
