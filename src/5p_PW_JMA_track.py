import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_mslp, get_pw, def_cmap, get_grads_JMA, draw_prapiroon

quick = True   
quick = False

if quick:
   res="c"
else:
   res="l"


def main( vtime_l=[], jvtime=datetime(2018, 7, 6, 0), adth=24 ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt = timedelta( hours=adth )
    

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    levs = np.arange( 20, 70, 2.5)
    levs = np.arange( 0, 62.5, 2.5)
    levs = np.arange( 0, 72.5, 2.5)
    clevs = np.arange( 800, 1200, 4 )

    fig, ((ax1,ax2,ax5), (ax3,ax4,ax6)) = plt.subplots( 2, 3, figsize=( 13.0, 6.0 ) )
    fig.subplots_adjust( left=0.03, bottom=0.02, right=0.95, top=0.97,
                         wspace=0.1, hspace=0.03)
    ax6.axis('off')

    ax_l = [ ax1, ax2, ax3, ax4 ]

    lons = 105
    lone = 165
    late = 50
    lats = 15

    lons = 111
    lone = 159
    late = 46
    lats = 19

    m_l = prep_proj_multi('merc', ax_l, res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )
 


    m5_l = prep_proj_multi('merc', [ ax5 ], res=res, ll_lon=lons, ur_lon=lone, 
             ll_lat=lats, ur_lat=late, fs=8 )

    cmap = plt.cm.get_cmap("GnBu")
    cmap = plt.cm.get_cmap("Blues")

    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar="PW" )
    x2d, y2d = m_l[0](lon2d, lat2d)

    pnum_l = [ "(a)", "(b)", "(c)", "(d)" ]

    for i, ax in enumerate( ax_l ):
        vtime = vtime_l[i]

        mslp = get_mslp( INFO, stime=vtime, vtime=vtime, m=0 )
        pw = get_pw( INFO, stime=vtime, vtime=vtime, m=0 )

        SHADE = ax.contourf( x2d, y2d, pw*0.001, 
                             cmap=cmap, extend='max',
                             levels=levs )

        CONT = ax.contour( x2d, y2d, mslp*0.01, colors='gainsboro',
                            linewidths=1.0, levels=clevs )
        ax.clabel( CONT, fontsize=8, fmt='%.0f' )
   
        ptit = "Analyzed PW & MSLP at {0:}".format( vtime.strftime('%HUTC %m/%d') )
        

        ax.text( 0.5, 1.01, ptit,
                 fontsize=10, transform=ax.transAxes,
                 horizontalalignment='center', 
                 verticalalignment='bottom',
                 ) #bbox = bbox)

        ax.text( 0.0, 1.01, pnum_l[i],
                 fontsize=9, transform=ax.transAxes,
                 horizontalalignment='left', 
                 verticalalignment='bottom',
                 )


    pos = ax4.get_position()
    cb_width = 0.008
    cb_height = pos.height*0.95
    ax_cb = fig.add_axes( [pos.x1+0.01, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
    cb.ax.tick_params( labelsize=8 )
 
    ax4.text( 0.98, 1.01, r'(mm/m$^2$)',
              fontsize=8, transform=ax4.transAxes,
              horizontalalignment='left', 
              verticalalignment='bottom',
              )



    # JMA
    jma2d, JMAr_lon, JMAr_lat = get_grads_JMA( jvtime - adt , adth, ACUM=True )

    jma2d[jma2d < 0.1] = np.nan
    rain = jma2d

    lon2d_jma, lat2d_jma = np.meshgrid( JMAr_lon, JMAr_lat )
    x2d, y2d = m5_l[0](lon2d_jma, lat2d_jma) 

    levs = np.arange( 10, 155, 5 )
    cmap = plt.cm.get_cmap("jet")

    cmap.set_under('gray',alpha=1.0)
    extend = 'both'

    SHADE = ax5.contourf( x2d, y2d, rain, levels=levs, cmap=cmap,
                          extend=extend)

    pos = ax5.get_position()
    cb_width = 0.008
    cb_height = pos.height*0.95
    ax_cb = fig.add_axes( [pos.x1+0.01, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
    cb.ax.tick_params( labelsize=8, )
 
    ax5.text( 0.98, 1.01, "(mm/24h)",
              fontsize=8, transform=ax5.transAxes,
              horizontalalignment='left', 
              verticalalignment='bottom',
              )

    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    xof = -72
    yof = 10

    _, _, _ = draw_prapiroon( m5_l[0], ax5, time=vtime,
                              c='gray', c_track='k', ms=0.0, marker='x', 
                              lw=3.0, ms_track=0.0, label="JMA best track\nPrapiroon (2018)" )
    ax5.legend( loc='lower right', fontsize=9 )

    arrowprops = dict(
       arrowstyle="->",
       connectionstyle="angle,angleA=0,angleB=-45,rad=10")
    

    for i, vtime_ in enumerate( vtime_l ):

        tlon, tlat, _ = draw_prapiroon( m5_l[0], ax5, time=vtime_,
                                  c='k', c_track='k', ms=0.0, marker='x', 
                                  lw=0.0, ms_track=0.0 )
        tx, ty = m5_l[0](tlon, tlat)
    
    
        ax5.annotate( "{0:} {1:}".format( pnum_l[i], vtime_.strftime('%m/%d') ),
                      xy=( tx, ty ),
                      xytext=( xof, yof ),
                      textcoords='offset points', #"'offset points', 
                      arrowprops=arrowprops,
                      fontsize=9,
                      bbox=bbox )
  
#    ax5.text( tx-0.1, ty+0.1, "7/3",
#              fontsize=10, transform=ax5.transData,
#              ha='right', va='bottom',
#              bbox=bbox,
#              )



    ptit = 'JMA radar accumulated precipitation on {0:}'.format( ( jvtime - adt ).strftime('%m/%d') )

    ax5.text( 0.5, 1.01, ptit,
              fontsize=10, transform=ax5.transAxes,
              horizontalalignment='center', 
              verticalalignment='bottom',
              )

    ax5.text( 0.0, 1.01, "(e)",
              fontsize=9, transform=ax5.transAxes,
              horizontalalignment='left', 
              verticalalignment='bottom',
              )

    ofig = "5p_PW_JMA_track"
    if not quick:
       opath = "png/fig0808"
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()
    

time = datetime( 2018, 6, 26, 0 )
etime = datetime( 2018, 7, 6, 0 )

vtime_l = [
           datetime( 2018, 7, 2, 0), 
           datetime( 2018, 7, 3, 0), 
           datetime( 2018, 7, 4, 0), 
           datetime( 2018, 7, 5, 0), 
          ]

main( vtime_l=vtime_l )
