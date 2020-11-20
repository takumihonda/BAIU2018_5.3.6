import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
from tools_BAIU import get_lonlat, get_var, get_prapiroon, read_etrack


quick = True   
#quick = False


ng = 3
kernel = np.ones( (ng,ng)) / (ng**2)

def main( 
          ctime=datetime( 2018, 7, 5, 0 ), 
          stime=datetime( 2018, 7, 5, 0 ), 
          stime_ref=datetime( 2018, 6, 27, 0 ), 
          dlon=1.0,
          adt_h = 24,
          vtime_ref=datetime( 2018, 7, 6, 0 ),
          ):


    mmax = 50 # debug


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

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

    fig, ( ( ax1, ax2 ) ) = plt.subplots( 1, 2, figsize=( 11, 5.0 ) )
    fig.subplots_adjust( left=0.1, bottom=0.1, right=0.97, top=0.95,
                         wspace=0.15, hspace=0.2)


    blon, blat, bmslp = get_prapiroon( time=ctime )

    tclat_l_ = []
    tclon_l_ = []
    tcslp_l_ = []

    #for m in range( mmax ):
    for i, mem in enumerate( mem_l[:] ):
        print( mem, rain_l[i])

        tclat_l_.append( tclat_l[mem,cit] )
        tclon_l_.append( tclon_l[mem,cit] )
        tcslp_l_.append( tcmslp_l[mem,cit] )


    tclon_l = np.array( tclon_l_)
    tclat_l = np.array( tclat_l_)
    tcslp_l = np.array( tcslp_l_)

    err_l = np.sqrt( np.square( tclon_l[:] - blon ) + 
                     np.square( tclat_l[:] - blat ) )

    print( tcslp_l )
#    err_l = tcslp_l[:] - bmslp 


#    err_l[ tclat_l > 40.0 ] = np.nan

    #ax1.scatter( tclat_l_, rain_l )
    ax1.scatter( tcslp_l, rain_l, c=rain_l, cmap="jet" )
    ax2.scatter( err_l, rain_l, c=rain_l, cmap="jet"  )
#    ax1.scatter( tclon_l, rain_l )
#    ax1.scatter( tclat_l, rain_l )

#    xlab = "TC longitude (deg)"
    xlab = "TC SLP valid at {0:} (hPa)".format( ctime.strftime('%HUTC %m/%d'), )
    xlab2 = "TC position error valid at {0:} (deg)".format( ctime.strftime('%HUTC %m/%d'), )
    ylab = "Forecast precipitation amount (mm)"
    ax1.set_ylabel( ylab, fontsize=12 )
    ax1.set_xlabel( xlab, fontsize=12 )
    ax2.set_xlabel( xlab2, fontsize=12 )


    note = "Period: {0:}\n-{1:}".format( ( vtime_ref - timedelta(hours=adt_h) ).strftime('%HUTC %m/%d'),
              vtime_ref.strftime('%HUTC %m/%d'), )
    ax1.text( 0.99, 0.8, note,
              fontsize=10, transform=ax1.transAxes,
              ha='right', va='top',
              )



    tit = "Initial: {0:}".format( stime.strftime('%HUTC %m/%d') )
    fig.suptitle( tit, fontsize=14 )

#    ax1.text( 0.99, 0.99, Initl,
#              fontsize=12, transform=ax1.transAxes,
#              ha='right', va='top', )

    opath = "png/track"
    ofig = "2p_scat_track_s{0:}_dlon{1:}_ng{2:0=3}_{3:}".format( stime.strftime('%m%d'), dlon, ng, ctime.strftime('%m%d%H'),  ) 

    if not quick:

       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()


    sys.exit()






#    plt.scatter( tclat_l_, rain_l[::-1] )
#    plt.show()
#    plt.scatter( tclon_l_, rain_l[::-1] )
#    plt.show()


##################

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 5, 0 )

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 3, 0 )
#stime = datetime( 2018, 7, 3, 0 )
stime = datetime( 2018, 7, 2, 0 )
stime = datetime( 2018, 7, 1, 0 )
stime = datetime( 2018, 6, 30, 0 )
etime = stime

dlon = 1.0
dlon = 2.0
#dlon = 3.0

# TC mark
ctime = datetime( 2018, 7, 6, 0 )
ctime = datetime( 2018, 7, 1, 0 )
#ctime = datetime( 2018, 7, 6, 0 )
ctime = datetime( 2018, 6, 30, 0 )
#ctime = datetime( 2018, 7, 2, 0 )
#ctime = datetime( 2018, 7, 1, 0 )


adt_h = 48
vtime_ref = datetime( 2018, 7, 7, 0 )

#stime = etime

time = stime
while time <= etime:
    main( 
          ctime=ctime,
          stime=time,
          dlon=dlon,
          adt_h=adt_h,
          vtime_ref=vtime_ref,
           )
    
    time += timedelta( days=1 )

