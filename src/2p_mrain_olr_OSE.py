import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_var, def_cmap, draw_rec

from scipy.interpolate import griddata

quick = True   
#quick = False


def main( stime=datetime( 2018, 6, 30, 0), 
          vtime=datetime( 2018, 7, 5, 0 ), nvar="RAIN", nvar2="MSLP", 
          ovtime=datetime( 2018, 7, 5, 0 ),
          adt_h=24, cmem=10, dth2=0,
          hpa=950, hpa2=950 ):

    #TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/NOVADWND"
    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/NOADPSFC"
    
    ptit_l = [ "{0:}-h RAIN {1:}".format( adt_h, vtime.strftime('%H UTC%m/%d'), ), 
               "OLR & MSLP {0:}".format( ovtime.strftime('%HUTC%m/%d'), ) ]

    adt = timedelta( hours=adt_h )
    
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }


    lon2d, lat2d = get_lonlat( INFO, stime=stime )


    pnum_l = [ "(a)", "(b)", "(c)", "(d)" ] 

    fig, ( ax1,ax2 ) = plt.subplots( 1, 2, figsize=( 8, 3.5 ) )
    fig.subplots_adjust( left=0.05, bottom=0.05, right=0.93, top=0.9,
                         wspace=0.2, hspace=0.3)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1, ax2, ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=6 )

    x2d, y2d = m_l[0](lon2d, lat2d)

    dth_ = 0
    if nvar == "RAIN":
       dth_ = dth2
    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa, dth=dth_ )

    cmap2, levs2, unit2, extend2, nvar2_, fac2 = def_cmap( nvar=nvar2, hpa=hpa2 )
    cmap3, levs3, unit3, extend3, nvar3_, fac3 = def_cmap( nvar="OLR", hpa=hpa2 )

    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    lw = 0.5
    lc = 'k'
    if nvar == "PW":
       lc = 'gainsboro' #darkgray'
       lw = 1.0


    for m in range( 50 ):
        if m == 0:
           var_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
           var2_ = get_var( INFO, nvar=nvar2, stime=stime, vtime=ovtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )
           var3_ = get_var( INFO, nvar="OLR", stime=stime, vtime=ovtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )
        else:
           var_ += get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth_ ), hpa=hpa )
           var2_ += get_var( INFO, nvar=nvar2, stime=stime, vtime=ovtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )
           var3_ += get_var( INFO, nvar="OLR", stime=stime, vtime=ovtime, m=m+1, adt=timedelta( hours=0 ), hpa=hpa2 )


    var_ = var_ / 50
    var2_ = var2_ / 50
    var3_ = var3_ / 50

    var_l = [ var_, var3_ ]

    fac_l = [ fac, fac3 ]
    cmap_l = [ cmap, cmap3 ]
    levs_l = [ levs, levs3 ]
    unit_l = [ unit, unit3 ]

    extend_l = [ extend, extend3 ]

    for i, ax in enumerate( ax_l ):
       ptit = ptit_l[i]

       ax.text( 0.5, 1.01, ptit,
                fontsize=10, transform=ax.transAxes,
                ha='center', 
                va='bottom',
                zorder=5,
                bbox = bbox )


       SHADE = ax.contourf( x2d, y2d, var_l[i]*fac_l[i], 
                            cmap=cmap_l[i], levels=levs_l[i], extend=extend_l[i] )

       CONT = ax.contour( x2d, y2d, var2_*fac2, colors=lc,
                          linewidths=lw, levels=levs2 )
      
       ax.clabel( CONT, fontsize=6, fmt='%.0f' )
 

       draw_rec( m_l[0], ax, slon, elon, slat, elat,
                 c='k', lw=1.0, ls='solid' )
  

       pos = ax.get_position()
       cb_width = 0.01
       cb_height = pos.height*0.95
       ax_cb = fig.add_axes( [pos.x1+0.005, pos.y1-cb_height, cb_width, cb_height] )
       cb = plt.colorbar( SHADE, cax=ax_cb, 
                          orientation = 'vertical', ticks=levs_l[i][::2] )
       cb.ax.tick_params( labelsize=7 )

       ax.text( 0.95, 1.01, unit_l[i],
                fontsize=9, transform=ax.transAxes,
                horizontalalignment='left', 
                verticalalignment='bottom', )

       ax.text( 0.05, 0.98, pnum_l[i],
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='left', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )


 
    ofig = "2p_{0:}_{1:}_{2:}_{3:}_adt{4:0=3}".format( nvar_, nvar2_, vtime.strftime('v%H%m%d'), stime.strftime('s%H%m%d'), adt_h, )
    #gtit = "{0:} & {1:}, init:{2:}, valid:{3:}".format( nvar_, nvar2_, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
    gtit = "Init:{0:}".format( stime.strftime('%HUTC %m/%d'), )
   
    fig.suptitle( gtit, fontsize=12)

    if not quick:
       #opath = "png/2p_mrain_olr_NOVADWND"
       opath = "png/2p_mrain_olr_NOADPSFC"
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()



#####################




nvar_l = [
          #"OLR", 
          #"Q1_vg", 
          #"VORT", 
          "RAIN", 
         ]

nvar2_l = [
          "MSLP", 
          #"Z", 
          ]
 
hpa_l = [  
          #850, 
          500, 
        ]

adt_h = 24

adt_h = 48

ovtime = datetime( 2018, 7, 3, 0 )
ovtime = datetime( 2018, 7, 5, 0 )

# only for RAIN
dth2 = 48


stime = datetime( 2018, 7, 2, 18)
stime = datetime( 2018, 7, 2, 12 )
#stime = datetime( 2018, 7, 2, 6 )
#stime = datetime( 2018, 7, 2, 0 )

stime_l = [ 
            datetime( 2018, 7, 2, 18,),
          ]

vtime = datetime( 2018, 7, 7, 0, 0 )

for stime in  stime_l:
    for i, nvar in enumerate( nvar_l ):

        nvar2 = nvar2_l[i]
        hpa = hpa_l[i]
        hpa2 = hpa
    
        main( stime=stime, vtime=vtime, nvar=nvar, nvar2=nvar2, 
              hpa=hpa, hpa2=hpa2, adt_h=adt_h, dth2=dth2,
              ovtime=ovtime )

