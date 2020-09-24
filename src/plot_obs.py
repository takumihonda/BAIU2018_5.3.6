import numpy as np

from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

from tools_BAIU import read_obs_letkf, read_obsdep_letkf, prep_proj_multi

quick = True
quick = False




def main(time):

    #obs_all = read_obs_letkf(time)
    obs_all = read_obsdep_letkf( time )


    print( "# of Obs: ", len( obs_all[:,0] ) )


    fig, (ax1) = plt.subplots( 1, 1, figsize=( 7.0, 6.0) )
    fig.subplots_adjust( left=0.08, bottom=0.02, right=0.98, top=0.97, wspace=0.2, hspace=0.1)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1, ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone,
                          ll_lat=lats, ur_lat=late, fs=6 )

    obstype_n = ['ADPUPA', 'AIRCAR', 'AIRCFT', 'SATWND', 'PROFLR',
                 'VADWND', 'SATEMP', 'ADPSFC', 'SFCSHP', 'SFCBOG', 
                 'SPSSMI', 'SYNDAT', 'ERS1DA', 'GOESND', 'QKSWND',
                 'MSONET', 'GPSIPW', 'RASSDA', 'WDSATR', 'ASCATW',
                 'TMPAPR', 'PHARAD', 'H08IRB', 'TCVITL' 
                 ]
    obstype_l = np.arange( 1, 25, 1 )
    obstype_c = [ 'cyan','brown','purple','y','k',
                  'r','lime','b','g','w',
                  'w','w','w','w','w',
                  'w','w','w','w','aqua',
                  'w','w','w','w' ]

    total = 0
    for otyp in range( len( obstype_l ) ):

       idx_tmp = np.where( (obs_all[:,6] == otyp+1 ) & 
                           (obs_all[:,1] >= lons ) &
                           (obs_all[:,1] <= lone ) &
                           (obs_all[:,2] >= lats ) &
                           (obs_all[:,2] <= late ) )

       print( otyp+1, obstype_n[otyp], len( idx_tmp[0] ), obstype_c[otyp] )
       xs, ys = m_l[0]( obs_all[idx_tmp,1], obs_all[idx_tmp,2] )
       if len(idx_tmp[0]) > 0:
         total += len(idx_tmp[0])
         ms = 2.0
         ec = None
         if len(idx_tmp[0]) < 15000:
            ms = 30.0
            if obstype_n[otyp] == "ADPSFC":
               ms = 5.0
            elif obstype_n[otyp] == "ADPUPA":
               ms = 20.0
               ec = None
            elif obstype_n[otyp] == "SFCSHP":
               ms = 15.0
            elif obstype_n[otyp] == "VADWND":
               ms = 40.0


         ax1.scatter( xs, ys, c=obstype_c[otyp], s=ms,
                      label=obstype_n[otyp] + ": " + str( len( idx_tmp[0] ) ),
                      edgecolors=ec,linewidths=0.5 )

    print( "Total: ",total )

    LEG = ax1.legend(loc='upper right')
    LEG.get_frame().set_alpha(0.8)

    tit = "Assimilated observations at {0:}".format( time.strftime('%HUTC %m/%d/%Y') )

    fig.suptitle(tit, fontsize=14)

    ofig = "1p_obs_" + time.strftime('%m%d%H') 


    if not quick:
       opath = "png/1p_obs"
       os.makedirs( opath, exist_ok=True )
       ofig = os.path.join( opath, ofig + ".png" )
       plt.savefig( ofig, bbox_inches="tight", pad_inches = 0.1 )
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()


####################




stime = datetime( 2018, 7, 2, 6 )
etime = datetime( 2018, 7, 3, 0 )
#etime = stime

time = stime
while( time <= etime):
  main(time)
  time += timedelta(hours=6)
