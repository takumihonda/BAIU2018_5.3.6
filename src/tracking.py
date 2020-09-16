import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
 
from tools_BAIU import get_lonlat, get_var, prep_proj_multi, get_prapiroon, convolve_ave


quick = True   
quick = False

if quick:
   res="c"
else:
   res="l"

ng = 3
kernel = np.ones( (ng,ng)) / (ng**2)

def main( 
          dlon = 1.0,
          stime=datetime( 2018, 7, 5, 0 ), 
          stime_ref=datetime( 2018, 6, 27, 0 ), 
          etime_ref=datetime( 2018, 7, 5, 0 ), ):

    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    fig, ( ax1 ) = plt.subplots( 1, 1, figsize=( 8, 6.5 ) )
    fig.subplots_adjust( left=0.06, bottom=0.07, right=0.97, top=0.95,
                         wspace=0.15, hspace=0.2)



    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    INFO = {"TOP": TOP, }
    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )


    blon, blat, btime_ref =  get_prapiroon( time=datetime( 2018, 6, 28, 0) ) 
    mmax = 50 # debug
#    mmax = 20 # debug

    time_l = []
    time = stime_ref
    while time <= etime_ref:
       time_l.append( time )

       time += timedelta( hours=6 )

    tmax = len( time_l )

    tclon_l = np.zeros( (mmax, tmax ))
    tclat_l = np.zeros( (mmax, tmax ))
    tcmslp_l = np.zeros( (mmax, tmax ))

    tclon_l[:] = np.nan
    tclat_l[:] = np.nan
    tcmslp_l[:] = np.nan

    for m in range( mmax ): 
       print( m + 1 )

       cnt  = 0

       vtime = stime
       while vtime <= etime_ref:
           blon, blat, _ =  get_prapiroon( time=vtime ) 

           mslp_ = get_var( INFO, nvar="MSLP", stime=stime, vtime=vtime, m=m+1 )
           mslp_ = convolve_ave( mslp_, kernel )

           if vtime >= btime_ref:
              if cnt == 0:       
                 mslp_[ ( np.abs( lon2d - blon ) > dlon ) | 
                        ( np.abs( lat2d - blat ) > dlon ) ] = np.nan
              else:
                 mslp_[ ( np.abs( lon2d - tclon ) > dlon ) | 
                        ( np.abs( lat2d - tclat ) > dlon ) ] = np.nan
              cy, cx = np.unravel_index( np.nanargmin(mslp_), mslp_.shape ) 
              tclon, tclat = lon2d[cy,cx], lat2d[cy,cx] 
              tcmslp = mslp_[cy,cx]
 
              if tcmslp > 1000.0:
                 vtime += timedelta( hours=6 )
                 if cnt < 1:
                    continue
                 else:
                    break

              cnt += 1

              for it, time_ in enumerate( time_l ):
                  dt = ( time_ - vtime ).total_seconds()
                  if dt == 0.0:
                     break
              tclon_l[m,it] = tclon
              tclat_l[m,it] = tclat
              tcmslp_l[m,it] = tcmslp

           vtime += timedelta( hours=6 )


    opath = "dat/track"
    os.makedirs( opath, exist_ok=True )

    of = "track_s{0:}_ng{1:0=3}_dlon{2:}".format( stime.strftime('%m%d'), ng, dlon )


    if quick:
       for m in range( mmax ):
          plt.plot( tclon_l[m,:], tclat_l[m,:], markersize=3.0, marker='o' )
       plt.show()
       for m in range( mmax ):
           plt.plot( time_l[:], tcmslp_l[m,:] )
       plt.show()
    else:
       print( of )
       np.savez( os.path.join( opath, of), tclon_l=tclon_l, 
              tclat_l=tclat_l, time_l=time_l, tcmslp_l=tcmslp_l )

##################

stime = datetime( 2018, 7, 1, 0 )
stime = datetime( 2018, 6, 27, 0 )
#etime = datetime( 2018, 7, 5, 0 )

#stime = datetime( 2018, 6, 30, 0 )
etime = stime

etime_ref = datetime( 2018, 7, 6, 0 )

#stime = datetime( 2018, 6, 29, 0 )
#etime = stime

dlon = 1.0
dlon = 2.0
#dlon = 3.0

time = stime
while time <= etime:
    main( 
          stime=time,
          etime_ref=etime_ref,
          dlon=dlon,
           )
    
    time += timedelta( days=1 )

