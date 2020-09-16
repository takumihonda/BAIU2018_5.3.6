import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp, get_gph, get_prsvar, get_dlm, get_prapiroon

from scipy.interpolate import griddata

quick = True   
quick = False

TC = True

def main( stime=datetime( 2018, 6, 30, 0), 
          vtime=datetime( 2018, 7, 5, 0 ) ):

    nvar = "Vprs"
    #nvar = "Uprs"


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

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    # TC location in Best track
    tlon, tlat, ttime=  get_prapiroon( time=vtime )
    print( tlon, tlat, ttime )

    dist = np.sqrt( np.square(lon2d - tlon) + np.square(lat2d - tlat) )

    # TC grid indices
    tj, ti =  np.unravel_index( dist.argmin(), dist.shape ) 
    print( lon2d[tj,ti], lat2d[tj,ti])

    # radius for average
    radius = 5.0 # deg
    dist = np.where( dist > radius, np.nan, 1.0 )

    fac = 1.0
    unit = r'(ms$^{-1}$)'
    clevs = np.arange( -18, 20, 2 )
    clevs_dif = np.arange( -9, 10, 1 )
    

    # better member
    v_b = 0.0
    u_b = 0.0

    # worse member
    v_w = 0.0
    u_w = 0.0

    mem_max = 20
    for m in mem_l[0:mem_max]:
        print( "better ", m+1 )
        u_, v_ = get_dlm( INFO, stime=stime, vtime=vtime, m=m+1, dist=dist ) 
        u_b += u_
        v_b += v_

    print("")
    for m in mem_l[len(mem_l)-mem_max:len(mem_l):1]:
        print( "worse ",m )
        u_, v_ = get_dlm( INFO, stime=stime, vtime=vtime, m=m+1, dist=dist ) 
        u_w += u_
        v_w += v_


    u_b = u_b / mem_max
    v_b = v_b / mem_max
    u_w = u_w / mem_max
    v_w = v_w / mem_max

    print( u_b )
    print( 'Better U: {0:.2f}, V:{1:.2f}'.format( u_b, v_b ) )
    print( 'Worse U: {0:.2f}, V:{1:.2f}'.format( u_w, v_w ) )


    fig, ( (ax1) ) = plt.subplots( 1, 1, figsize=( 6, 5.5 ) )
    fig.subplots_adjust( left=0.1, bottom=0.1, right=0.9, top=0.93,
                         wspace=0.1, hspace=0.02)

    
    ax1.quiver( 0., 0., u_b, v_b, color='b', 
                scale=1, scale_units='xy', angles='xy', label='Better' )

    ax1.quiver( 0., 0., u_w, v_w, color='k', 
                scale=1, scale_units='xy', angles='xy', label='Worse' )

    xmin = -8
    xmax = 8
    ymin = -8
    ymax = 8
    ax1.set_xlim( xmin, xmax )
    ax1.set_ylim( ymin, ymax )

    xlab = r'Zonal wind (m s$^{-1}$)'
    ylab = r'Meridional wind (m s$^{-1}$)'

    ax1.set_xlabel( xlab, fontsize=12 )
    ax1.set_ylabel( ylab, fontsize=12 )
    ax1.grid()

    ax1.legend( loc='lower right', fontsize=12 )

    tit = "Composite deep layer mean wind"
    ax1.set_title( tit, size=13, loc = 'center' )


    note = "Init:{0:}\nvalid:{1:}".format( stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )

    bbox = {'facecolor':'w', 'alpha':0.9, 'pad':2}
    ax1.text( 0.01, 0.99, note, 
             fontsize=10, transform=ax1.transAxes,
             horizontalalignment='left', 
             verticalalignment='top',
             bbox = bbox)

    ofig = "1p_DLMW" + vtime.strftime('_v%H%m%d') 

    print( ofig )

    if not quick:
       opath = "png/comp_mem" + stime.strftime('_s%H%m%d')
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       plt.clf()
    else:
       plt.show()


###################

stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 6, 29, 0)
#stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 26, 0)
#stime = datetime( 2018, 6, 27, 0)
#stime = datetime( 2018, 6, 29, 0)
#stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)

etime = datetime( 2018, 7, 1, 0 )

time = stime
while time <= etime:
   main( stime=stime, vtime=time )

   time += timedelta( days=1 )
