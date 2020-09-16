import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
 
from tools_BAIU import get_lonlat, get_arain, get_pw

from scipy.interpolate import griddata

quick = True   
quick = False


def main( stime=datetime( 2018, 6, 30, 0), 
          vtime=datetime( 2018, 7, 5, 0 ) ):

    nvar = "Vprs"
    #nvar = "Uprs"


    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    

    vtime_ref = datetime( 2018, 7, 6, 0, 0, 0 )
    vtime = datetime( 2018, 7, 5, 0, 0, 0 )

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

    print( mem_l )
    print( np.max(mem_l), np.min(mem_l) )
    print( len(mem_l) )

    lon2d, lat2d = get_lonlat( INFO, stime=stime )

    pw_l = np.zeros( 50 )
    rain_l = np.zeros( 50 )

#    slon = 128.0
#    elon = 137.5
#    slat = 30.0
#    elat = 36.0

    for m in mem_l[:]:
        print( m )
        rain_ = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )

        pw_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1, )
        pw_l[m] = np.mean( pw_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )

    
    fig, ( (ax1) ) = plt.subplots( 1, 1, figsize=( 6, 5.5 ) )
    fig.subplots_adjust( left=0.1, bottom=0.1, right=0.9, top=0.93,
                         wspace=0.1, hspace=0.02)

    xmin = 40
    xmax = 65
    ymin = 0
    ymax = 60
    ax1.set_xlim( xmin, xmax )
    ax1.set_ylim( ymin, ymax )

    xlab = r'Precipitable water'
    ylab = r'Area-averaged {0:}-precipitation amount'.format( adt_h )

    ax1.set_xlabel( xlab, fontsize=12 )
    ax1.set_ylabel( ylab, fontsize=12 )

    print( ts_l.shape )
#    ax1.scatter( pw_l, ts_l )
    ax1.scatter( pw_l*0.001, rain_l )

    tit = "PW vs Precipitation"
    ax1.set_title( tit, size=13, loc = 'center' )


    ofig = "1p_scat" + stime.strftime('_s%H%m%d') + vtime.strftime('_v%H%m%d') + vtime_ref.strftime('_vr%H%m%d')  

    print( ofig )

    if not quick:
       opath = "png/scat"
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       plt.clf()
    else:
       plt.show()


    sys.exit()





    



###################

stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 26, 0)
#stime = datetime( 2018, 6, 27, 0)
#stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)

etime = datetime( 2018, 7, 1, 0 )

time = stime
main( stime=stime, vtime=time )

