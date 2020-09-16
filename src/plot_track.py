import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
from tools_BAIU import get_lonlat, get_var, prep_proj_multi, get_prapiroon, convolve_ave, draw_prapiroon, read_etrack


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
          stime_ref=datetime( 2018, 6, 27, 0 ), 
          dlon=1.0,
          vtime_ref=datetime( 2018, 7, 6, 0 ),
          etime_ref=datetime( 2018, 7, 5, 0 ), ):


    mmax = 50 # debug


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    adt_h = 24
    adt = timedelta( hours=adt_h )

    # get rain ensemble
    rain_l = np.zeros( mmax )

    # get reference
    for m in range( mmax ):
        #rain_ = get_arain( INFO, stime=stime, vtime=vtime_ref, adt=adt, m=m+1 )
        rain_ = get_var( INFO, nvar="RAIN", stime=stime, vtime=vtime_ref, m=m+1, adt=adt )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )


#    print( rain_l )

    mem_l = np.argsort( rain_l )[::-1]
    rain_l = np.sort( rain_l )[::-1]



    tclon_l, tclat_l, tcmslp_l, time_l = read_etrack( stime=stime,
                           ng=ng, dlon=dlon )

    for i, time_ in enumerate( time_l ):
        dt = ( time_ - ctime ).total_seconds()
        if dt == 0.0:
           cit = i

    fig, ( ax1 ) = plt.subplots( 1, 1, figsize=( 8, 6.0 ) )
    fig.subplots_adjust( left=0.06, bottom=0.07, right=0.97, top=0.95,
                         wspace=0.15, hspace=0.2)

    lons = 111
    lone = 159
    late = 46
    lats = 19

    m_l = prep_proj_multi('merc', [ ax1 ], res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )

    top_m = 5
    mmax = 50
    lw = 1.0
    ms = 6.0
    lw = 0.5
    ms = 9.0

    tclat_l_ = []
    tclon_l_ = []

    #for m in range( mmax ):
    for i, mem in enumerate( mem_l[::-1] ):

        print( i, mem, rain_l[-i-1] )
        if i == 0:
           lab_c = "Forecast at {0:}".format( ctime.strftime('%HUTC %m/%d') )
        else:
           lab_c = None

        xs_, ys_ = m_l[0]( tclon_l[mem,:], tclat_l[mem,:] )
        tclat_l_.append( tclat_l[mem,cit] )
        tclon_l_.append( tclon_l[mem,cit] )

        cc = cm.jet( ( i + 1 ) / mmax )
        cc2 = cc

#        cc = 'k'
#        cc2 = 'r'

#        lw = 4.0
#        if i < top_m:
#          cc = "b"
#          lw = 6.0
#        elif i >= ( mmax - top_m ):
#          cc = 'r'
#          lw = 6.0
#        else:
        m_l[0].plot( xs_, ys_, color=cc, linewidth=lw )  
        # ctime
        m_l[0].plot( xs_[cit], ys_[cit], color=cc2, marker="o",
               markersize=ms, label=lab_c )  

    draw_prapiroon( m_l[0], ax1, ms=10.0, lw=2.0, marker="o", c='gray',
                    ms_track=0.0, time=ctime, c_track='gray', label='Best track at {0:}'.format( ctime.strftime('%HUTC %m/%d') ) )

    ax1.legend( loc='lower right', )

    tit = "Initial {0:}".format( stime.strftime('%m/%d') )
    fig.suptitle( tit, fontsize=14 )


    opath = "png/track"
    ofig = "1p_track_s{0:}_dlon{1:}_ng{2:0=3}_{3:}".format( stime.strftime('%m%d'), dlon, ng, ctime.strftime('%m%d%H'),  ) 

    if not quick:

       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()

#    plt.scatter( tclat_l_, rain_l[::-1] )
#    plt.show()
#    plt.scatter( tclon_l_, rain_l[::-1] )
#    plt.show()


##################

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 5, 0 )

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 3, 0 )
stime = datetime( 2018, 6, 30, 0 )
stime = datetime( 2018, 7, 1, 0 )
stime = datetime( 2018, 7, 3, 0 )
#etime = stime

dlon = 1.0
dlon = 2.0
#dlon = 3.0

# TC mark
ctime = datetime( 2018, 7, 6, 0 )
ctime = datetime( 2018, 6, 30, 0 )
ctime = datetime( 2018, 7, 5, 0 )
#ctime = datetime( 2018, 7, 5, 0 )

#stime = etime

time = stime
while time <= etime:
    main( 
          ctime=ctime,
          stime=time,
          dlon=dlon,
           )
    
    time += timedelta( days=1 )

