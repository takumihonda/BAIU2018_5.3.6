import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
from tools_BAIU import get_lonlat, read_etrack, get_steering_flow, get_rain_idx


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
          adt_h=24,
          dlon=1.0, ):


    mmax = 50 # debug


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    rain_l, mem_l = get_rain_idx( INFO, slon=130.0, elon=137.5, 
                      slat=33.0, elat=36.0, vtime_ref=vtime_ref, stime=stime,
                      adt_h=adt_h, mmax=50, )

    tclon_l, tclat_l, tcmslp_l, time_l = read_etrack( stime=stime,
                           ng=ng, dlon=dlon )

    stu = np.zeros( tclon_l.shape )
    stv = np.zeros( tclon_l.shape )

    stu[:,:] = np.nan
    stv[:,:] = np.nan

    # Chan and Grey 1992MWR
    tc_rad = 5.0
    hpa_l = [ 500, 750 ]

    opath = "dat/track"
    of = "steering_flow_track_s{0:}_ng{1:0=3}_dlon{2:}_tcrad{3:}_hpa{4:}_{5:}.npz".format( stime.strftime('%m%d'), int( ng ), dlon, tc_rad, hpa_l[0], hpa_l[-1] )

    try:
       data = np.load( os.path.join( opath, of), allow_pickle=True ) 
       stu = data['stu']
       stv = data['stv']
    except:

       for m in range( mmax ):
           print( m )
           for t, time_ in enumerate( time_l ):
               if np.isnan( tclon_l[m,t] ):
                  continue
               stu[m,t], stv[m,t] = get_steering_flow( INFO, m=m, 
                                         lon2d=lon2d, lat2d=lat2d,
                                         stime=stime, vtime=time_, 
                                         hpa_l=hpa_l, 
                                         tc_rad=tc_rad )
   
       np.savez( os.path.join( opath, of), stu=stu, stv=stv ) 


    for t, time_ in enumerate( time_l ):
        dt = ( time_ - ctime ).total_seconds()
        if dt == 0:
           tidx = t
           break


    stu_ = stu[:,tidx]
    stv_ = stv[:,tidx]

    fig, ( ax1 ) = plt.subplots( 1, 1, figsize=( 8, 7.0 ) )
    fig.subplots_adjust( left=0.06, bottom=0.07, right=0.97, top=0.95,
                         wspace=0.15, hspace=0.2)

    # Warm (better) => cool (worse)
    for m, mem in enumerate( mem_l[:] ):
        print( mem, rain_l[m] )

        cc = cm.jet( (len(mem_l)-m-1) / len(mem_l) ), 
        ax1.quiver( 0.0, 0.0, stu_[mem], stv_[mem], 
                    color=cc, alpha=0.3, width=0.005,
                    angles='xy', scale_units='xy', scale=1 )

    print( stu_[0], stv_[0] )
    xmin = -10
    xmax = 15
    ymin = -5
    ymax = 20
    ax1.set_xlim( xmin, xmax )
    ax1.set_ylim( ymin, ymax )

    ax1.vlines( x=0, ymin=ymin, ymax=ymax, color='gray', linestyle='dashed',
                lw=0.5 )

    ax1.hlines( y=0, xmin=xmin, xmax=xmax, color='gray', linestyle='dashed',
                lw=0.5 )

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
ctime = datetime( 2018, 7, 1, 0 )
ctime = datetime( 2018, 7, 3, 0 )
ctime = datetime( 2018, 7, 5, 0 )

vtime_ref = datetime( 2018, 7, 6, 0 )
adt_h = 24

vtime_ref = datetime( 2018, 7, 7, 0 )
adt_h = 48

stime = etime

time = stime
while time <= etime:
    main( 
          ctime=ctime,
          stime=time,
          dlon=dlon,
          vtime_ref=vtime_ref,
          adt_h=adt_h,
           )
    
    time += timedelta( days=1 )

