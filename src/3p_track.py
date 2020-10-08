import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
 
from tools_BAIU import get_lonlat, get_var, prep_proj_multi, get_prapiroon, convolve_ave, draw_prapiroon, read_etrack


quick = True   
quick = False

if quick:
   res="c"
else:
   res="l"

ng = 3
kernel = np.ones( (ng,ng)) / (ng**2)

def main( 
          ctime=datetime( 2018, 7, 5, 0 ), 
          stime_l=[datetime( 2018, 7, 5, 0 ) ], 
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




    fig, ( ( ax1, ax2, ax3 ) ) = plt.subplots( 1, 3, figsize=( 12, 4.2 ) )
    fig.subplots_adjust( left=0.06, bottom=0.02, right=0.97, top=0.98,
                         wspace=0.15, hspace=0.1)
 
    ax_l = [ ax1, ax2, ax3 ]
 
    lons = 114
    lone = 146
    late = 46
    lats = 19

    m_l = prep_proj_multi('merc', ax_l, res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )

    top_m = 5
    mmax = 50
    lw = 0.5
    ms = 3.0

    tclat_l_ = []
    tclon_l_ = []

    mem_l = np.arange( 0, 50, 1 )

    for j, ax in enumerate( ax_l ):

        tclon_l, tclat_l, tcmslp_l, time_l = read_etrack( stime=stime_l[j],
                               ng=ng, dlon=dlon )
    
        for i, time_ in enumerate( time_l ):
            dt = ( time_ - ctime ).total_seconds()
            if dt == 0.0:
               cit = i


        for i, mem in enumerate( mem_l[::-1] ):
    
            if i == 0:
               lab_c = "Forecast at {0:}".format( ctime.strftime('%HUTC %m/%d') )
            else:
               lab_c = None
    
            xs_, ys_ = m_l[j]( tclon_l[mem,:], tclat_l[mem,:] )
            tclat_l_.append( tclat_l[mem,cit] )
            tclon_l_.append( tclon_l[mem,cit] )
    
            cc = cm.jet( ( i + 1 ) / mmax )
            cc2 = cc
    
            cc = 'k'
            cc2 = 'r'
    
    #        lw = 4.0
    #        if i < top_m:
    #          cc = "b"
    #          lw = 6.0
    #        elif i >= ( mmax - top_m ):
    #          cc = 'r'
    #          lw = 6.0
    #        else:
            m_l[j].plot( xs_, ys_, color=cc, linewidth=lw )  
            # ctime
            m_l[j].plot( xs_[cit], ys_[cit], color=cc2, marker="o",
                   markersize=ms, label=lab_c )  
    
        draw_prapiroon( m_l[j], ax, ms=10.0, lw=2.0, marker="o", c='b',
                        ms_track=0.0, time=ctime, c_track='b', label='Best track at {0:}'.format( ctime.strftime('%HUTC %m/%d') ) )
    
        ax.legend( loc='lower right', fontsize=8 )

        ptit = "Initial {0:}".format( stime_l[j].strftime('%m/%d') )
        ax.text( 0.5, 1.01, ptit,
                 fontsize=11, transform=ax.transAxes,
                 ha='center', 
                 va='bottom',
                )

#    fig.suptitle( tit, fontsize=14 )


    opath = "png/3p_track"
    ofig = "3p_track_dlon{0:}_ng{1:0=3}_{2:}".format( dlon, ng, ctime.strftime('%m%d%H'),  ) 

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

stime_l = [
           datetime( 2018, 6, 28, 0 ),
           datetime( 2018, 6, 30, 0 ),
           datetime( 2018, 7, 2, 0 ),
          ]

main( 
      ctime=ctime,
      stime_l=stime_l,
      dlon=dlon,
       )
    

