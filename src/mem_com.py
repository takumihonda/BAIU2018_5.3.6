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
quick = False

TC = True
TC = False

def main( stime=datetime( 2018, 6, 30, 0), vtime_ref=datetime( 2018, 7, 6, 0 ),
          vtime=datetime( 2018, 7, 5, 0 ), nvar="RAIN", nvar2="MSLP", 
          adt_h=24, mem_dif=0,
          hpa=950, hpa2=950 ):

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    

    adt = timedelta( hours=adt_h )
    
    slon = 130.0
    elon = 137.5
    slat = 33.0
    elat = 36.0

    INFO = {"TOP": TOP, }


    lon2d, lat2d = get_lonlat( INFO, stime=stime )


    rain_l = np.zeros( 50 )

    # get reference
    for m in range( 50 ):
        #rain_ = get_arain( INFO, stime=stime, vtime=vtime_ref, adt=adt, m=m+1 )
        rain_ = get_var( INFO, nvar="RAIN", stime=stime, vtime=vtime_ref, m=m+1, adt=adt )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )


    print( rain_l )
    #print( np.sort( rain_l )[::-1] )
    #print( np.argsort( rain_l )[::-1] )

    mem_l = np.argsort( rain_l )[::-1]
    rain_l = np.sort( rain_l )[::-1]

    print( mem_l )
    print( rain_l )

    print( "" )

    pmem_l = [ 
               mem_l[0+mem_dif], mem_l[1+mem_dif], 
               mem_l[-2-mem_dif], mem_l[-1-mem_dif] 
             ]

    pnum_l = [ "(a)", "(b)", "(c)", "(d)" ] 

    fig, ( (ax1,ax2), (ax3,ax4) ) = plt.subplots( 2, 2, figsize=( 8, 7 ) )
    fig.subplots_adjust( left=0.05, bottom=0.05, right=0.9, top=0.9,
                         wspace=0.1, hspace=0.3)

    lons = 105 + 6
    lone = 165 - 6
    late = 50
    lats = 16

    ax_l = [ ax1, ax2, ax3, ax4, ]# ax5, ax6 ]
    m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=6 )

    x2d, y2d = m_l[0](lon2d, lat2d)

    dth = 0
    if nvar == "RAIN":
       dth = adt_h
    cmap, levs, unit, extend, nvar_, fac = def_cmap( nvar=nvar, hpa=hpa )

    if nvar2 is not None:
       cmap2, levs2, unit2, extend2, nvar2_, fac2 = def_cmap( nvar=nvar2, hpa=hpa2 )

    bbox = {'facecolor':'w', 'alpha':1.0, 'pad':2}

    lw = 0.5
    lc = 'k'
    if nvar == "PW":
       lc = 'gainsboro' #darkgray'
       lw = 1.0
#    lc = 'w'


    for i, ax in enumerate( ax_l ):
       m = pmem_l[i]
       ptit = "Mem: {0:0=2}".format( m )

       var_ = get_var( INFO, nvar=nvar, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth ), hpa=hpa )
       SHADE = ax.contourf( x2d, y2d, var_*fac, 
                            cmap=cmap, levels=levs, extend=extend )

       if nvar2 is not None:
          var2_ = get_var( INFO, nvar=nvar2, stime=stime, vtime=vtime, m=m+1, adt=timedelta( hours=dth ), hpa=hpa2 )
          CONT = ax.contour( x2d, y2d, var2_*fac2, colors=lc,
                             linewidths=lw, levels=levs2 )
      
          ax.clabel( CONT, fontsize=6, fmt='%.0f' )
 
       if TC:
          time_l = []
          tcx_l = []
          tcy_l = []
          stime_ = vtime - timedelta( days=3 )
          time = vtime
          while time >= stime_:
              mslp_ = get_var( INFO, nvar="MSLP", stime=stime, vtime=time, m=m+1,)
              mslp_[ lon2d < 126.0 ] = np.nan
              cy, cx = np.unravel_index( np.nanargmin(mslp_), mslp_.shape ) 
              tcx, tcy = m_l[0]( lon2d[cy,cx], lat2d[cy,cx] )
              tcx_l.append( tcx )
              tcy_l.append( tcy )
              time_l.append( time )
              time -= timedelta( hours=6 )
#          print( lon2d[cy,cx], lat2d[cy,cx] )
          ax.plot( tcx_l, tcy_l, markersize=3, linewidth=2.0,
                   color='cyan', marker='o' )

          xof = -72
          yof = 10

          arrowprops = dict(
             arrowstyle="->",
             connectionstyle="angle,angleA=0,angleB=-45,rad=10",
             color='cyan')

          for j, time in enumerate( time_l ):
             if j % 4 != 0:
                continue
             ax.annotate( "{0:}".format( time.strftime('%HUTC %m/%d') ),
                           xy=( tcx_l[j], tcy_l[j] ),
                           xytext=( xof, yof ),
                           textcoords='offset points', #"'offset points', 
                           arrowprops=arrowprops,
                           fontsize=6,
                           bbox=bbox )

       draw_rec( m_l[0], ax, slon, elon, slat, elat,
                 c='k', lw=1.0, ls='solid' )
  

       if i == 1:
          pos = ax.get_position()
          cb_width = 0.01
          cb_height = pos.height*1.5
          ax_cb = fig.add_axes( [pos.x1+0.005, pos.y1-cb_height, cb_width, cb_height] )
          cb = plt.colorbar( SHADE, cax=ax_cb, 
                             orientation = 'vertical', ticks=levs[::2] )
          cb.ax.tick_params( labelsize=7 )

          ax.text( 0.95, 1.01, unit,
                   fontsize=9, transform=ax.transAxes,
                   horizontalalignment='left', 
                   verticalalignment='bottom', )

       if i == 0 or i == 2:
          if i == 0:
             ltit = "Best members"
          else:
             ltit = "Worst members"
          ax.text( 1.1, 1.05, ltit,
                   fontsize=14, transform=ax.transAxes,
                   horizontalalignment='center', 
                   verticalalignment='bottom', )


       ax.text( 0.5, 0.98, ptit,
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='center', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )

       ax.text( 0.05, 0.98, pnum_l[i],
                fontsize=10, transform=ax.transAxes,
                horizontalalignment='left', 
                verticalalignment='top',
                zorder=5,
                bbox = bbox )


 
    if nvar2 is not None:
       ofig = "4p_{0:}_{1:}_{2:}_adt{3:0=3}_memdif{4:0=3}".format( nvar_, nvar2_, vtime.strftime('v%H%m%d'), adt_h, mem_dif, mem_dif )
       gtit = "{0:} & {1:}, init:{2:}, valid:{3:}".format( nvar_, nvar2_, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
    else:
       ofig = "4p_{0:}_{1:}_{2:0=3}".format( nvar_, vtime.strftime('v%H%m%d'), adt_h )
       gtit = "{0:}, init:{1:}, valid:{2:}".format( nvar_, stime.strftime('%HUTC %m/%d'), vtime.strftime('%HUTC %m/%d') )
   
    fig.suptitle( gtit, fontsize=12)

    if not quick:
       opath = "png/4p_mem" + stime.strftime('_s%H%m%d')
       os.makedirs(opath, exist_ok=True)
     
       ofig = os.path.join(opath, ofig + ".png")
       plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
       print(ofig)
       plt.clf()
    else:
       print(ofig)
       plt.show()



#####################

stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)
#stime = datetime( 2018, 7, 3, 0)

vtime_l = [
           datetime( 2018, 7, 3, 0, 0 ),
           datetime( 2018, 7, 4, 0, 0 ),
           datetime( 2018, 7, 5, 0, 0 ),
           datetime( 2018, 7, 6, 0, 0 ),
          ]


nvar_l = [
          "PW", 
          "RAIN", 
          "THE", 
          "QV", 
          "QV", 
          "T", 
          "T", 
          ]

nvar2_l = [
          "MSLP", 
          "MSLP", 
          "Z", 
          "MSLP", 
          "Z", 
          "Z", 
          "Z", 
          ]

hpa_l = [ 950, 950, 950, 950, 500, 500, 300 ]



#nvar_l = [
##          #"RH",
#          "U",
#          "V",
#          "U",
#          "V",
#          "U",
#          "V",
#          "U",
#          "V",
#          "U",
#          "V",
##          #"QV",
#         ] 
##
#nvar2_l = [
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
#          "Z", 
##          #"MSLP", 
#          ]
#
#hpa_l = [ 950, 950, 850, 850, 700, 700, 500, 500, 300, 300 ]
##
##hpa_l = [ 850, 500, 300 ]
#hpa_l = [ 850, 850, ]
#hpa_l = [ 500, 500, ]
#hpa_l = [ 300, 300, ]


nvar_l = [
          "PW",
          "RAIN",
         ]

nvar2_l = [
          "MSLP", 
          "MSLP", 
          ]

hpa_l = [ 850, 850, ]

vtime_l = [
#           datetime( 2018, 7, 1, 0, 0 ),
#           datetime( 2018, 7, 2, 0, 0 ),
           datetime( 2018, 7, 3, 0, 0 ),
           datetime( 2018, 7, 4, 0, 0 ),
           datetime( 2018, 7, 5, 0, 0 ),
           datetime( 2018, 7, 6, 0, 0 ),
           datetime( 2018, 7, 7, 0, 0 ),
          ]

adt_h = 24
vtime_ref = datetime( 2018, 7, 6, 0 )

adt_h = 48
vtime_ref = datetime( 2018, 7, 7, 0 )

mem_dif = 2
#mem_dif = 4
#mem_dif = 6
#mem_dif = 8

for vtime in  vtime_l:
    for i, nvar in enumerate( nvar_l ):

        nvar2 = nvar2_l[i]
        hpa = hpa_l[i]
        hpa2 = hpa
    
        main( stime=stime, vtime_ref=vtime_ref, vtime=vtime, nvar=nvar, nvar2=nvar2, 
              hpa=hpa, hpa2=hpa2, adt_h=adt_h, mem_dif=mem_dif )

