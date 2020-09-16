import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
 
from tools_BAIU import get_lonlat, get_var, prep_proj_multi, get_grads_JMA, def_cmap, draw_rec


quick = True   
#quick = False

if quick:
   res="c"
else:
   res="l"


def main( 
          stime=datetime( 2018, 7, 5, 0 ), dth=24,
          vtime=datetime( 2018, 7, 5, 0 ),
          etime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):

    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    fig, ( ax1 ) = plt.subplots( 1, 1, figsize=( 8, 6.5 ) )
    fig.subplots_adjust( left=0.06, bottom=0.07, right=0.97, top=0.95,
                         wspace=0.15, hspace=0.2)



    fac = 1.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    cmap_, levs_, unit_, extend_, nvar_, fac_ = def_cmap( nvar=nvar, hpa=hpa )

    mmax = 50 # debug
    evar = np.zeros( ( mmax, lon2d.shape[0], lon2d.shape[1] ) )

    t = 0
    for m in range( mmax ): 
       evar[m,:,:] = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth ), hpa=hpa )



    lons = 111
    lone = 159
    late = 46
    lats = 19

    m_l = prep_proj_multi('merc', [ ax1 ], res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )

    x2d_, y2d_ = m_l[0](lon2d, lat2d) 

    levs = [ 980.0 ]

    for m in range( mmax ) :
#        ax1.contour( x2d_, y2d_, evar[m,:,:], levels=levs )
        mslp_ = evar[m,:,:]
        cy, cx = np.unravel_index( np.argmin(mslp_), mslp_.shape ) 

        x_, y_ = m_l[0]( lon2d[cy,cx], lat2d[cy,cx] )
        m_l[0].plot( x_, y_, marker='o', color='b',
                     markersize=10.0, )
        #print( lon2d[cy,cx], lat2d[cy,cx] )

    tit = "Initial: {0:} valid: {1:}".format( stime.strftime('%m/%d'), vtime.strftime('%m/%d')  )
    fig.suptitle( tit, fontsize=14 )

    opath = "png/mslp_mem"
    ofig = "1p_MSLP_v{0:}_s{1:}".format( vtime.strftime('%m%d'), stime.strftime('%m%d')  ) 

    if not quick:

       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()



etime = datetime( 2018, 7, 7, 0 )
#nvar = "RAIN"
adt = timedelta( hours=24 )


vtime = datetime( 2018, 6, 30, 0 )
#vtime = datetime( 2018, 7, 2, 0 )
#vtime = datetime( 2018, 7, 4, 0 )
#vtime = datetime( 2018, 7, 5, 0 )

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7,  4, 0 )
etime = datetime( 2018, 7,  2, 0 )

etime = vtime

nvar = "MSLP"

hpa = [ 500 ]

time = stime
while time <= etime:
    main( vtime=vtime,
          stime=time,
          nvar=nvar, hpa=hpa, etime=etime, )
    
    time += timedelta( days=1 )

