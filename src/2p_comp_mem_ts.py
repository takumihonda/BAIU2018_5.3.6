import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp, get_gph

from scipy.interpolate import griddata

quick = True   
#quick = False



def main():

    nvar = "MSLP"
    nvar = "Z"

    hpa = 500

    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    stime = datetime( 2018, 6, 30, 0, 0, 0 )
    stime = datetime( 2018, 6, 26, 0, 0, 0 )

    vtime = datetime( 2018, 7, 7, 0, 0, 0 )
    vtime = datetime( 2018, 7, 6, 0, 0, 0 )
    vtime = datetime( 2018, 7, 5, 0, 0, 0 )
    vtime = datetime( 2018, 7, 1, 0, 0, 0 )
#    vtime = datetime( 2018, 7, 3, 0, 0, 0 )
#    vtime = datetime( 2018, 7, 4, 0, 0, 0 )
#    vtime = datetime( 2018, 7, 5, 0, 0, 0 )
    

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
    elif nvar == "Z":
       clevs = np.arange( 0, 8000, 20 )
       fac = 1.0
       unit = "(m)"
    

    # better member
    var_b = np.zeros( lon2d.shape )

    # worse member
    var_w = np.zeros( lon2d.shape )

    mem_max = 20
    for m in mem_l[0:mem_max]:
        print( "better ", m )
        #var_b_ = get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )
        if nvar == "MSLP":
           var_b += get_mslp( INFO, stime=stime, vtime=vtime, m=m )
        elif nvar == "Z":
           var_b += get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )


    #print(mem_l[len(mem_l)-mem_max:len(mem_l):1])
    print("")
    for m in mem_l[len(mem_l)-mem_max:len(mem_l):1]:
        print( "worse ",m )
        if nvar == "MSLP":
           var_w += get_mslp( INFO, stime=stime, vtime=vtime, m=m )
        elif nvar == "Z":
           var_w += get_gph( INFO, stime=stime, vtime=vtime, m=m, hpa=hpa )

    var_b = var_b / mem_max
    var_w = var_w / mem_max


    fig, ((ax1,ax2)) = plt.subplots( 1, 2, figsize=( 9.5, 4.0 ) )
    fig.subplots_adjust( left=0.04, bottom=0.02, right=0.96, top=0.95,
                         wspace=0.2, hspace=0.02)

    lons = 105
    lone = 165
    late = 50
    lats = 15

    ax_l = [ ax1, ax2 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=7 )


    x2d, y2d = m_l[0](lon2d, lat2d)
 
    tit_l = [ "Better {0:} members".format( mem_max ), 
              "Worse {0:} members".format( mem_max ) ]
    var_l = [ var_b*fac, var_w*fac ]


    for i, ax in enumerate( ax_l ):

        if nvar == "MSLP" or nvar == "Z":
           CONT = ax.contour( x2d, y2d, var_l[i], colors='k',
                              linewidths=0.5, levels=clevs )
   
           ax.clabel( CONT, fontsize=7, fmt='%.0f' )
 
        ax.set_title( tit_l[i], size=12, loc = 'center' )
       

    if nvar == "Z":
       nvar += str( hpa )

    gtit = "Composite {0:} {1:}, init:{2:}, valid:{3:}".format( nvar, unit, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
    fig.suptitle( gtit, fontsize=14)


    ofig = "2p_" + nvar + vtime.strftime('_v%H%m%d') 
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









main()
