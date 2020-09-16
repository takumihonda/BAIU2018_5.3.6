import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_pw, get_gph, get_prsvar, get_the, get_rh, get_the_grad


quick = True   
#quick = False


def main( stime_l=[],
          vtime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):


    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    adt = timedelta( hours=24 )
    
    bbox = {'facecolor':'w', 'alpha':0.95, 'pad':2}

    INFO = {"TOP": TOP, }

    lon2d, lat2d = get_lonlat( INFO, stime=datetime( 2018, 7, 1, 0 ) )

    fig, ((ax1,ax2,ax3,ax4),(ax5,ax6,ax7,ax8)) = plt.subplots( 2, 4, figsize=( 14, 5.5 ) )
    fig.subplots_adjust( left=0.03, bottom=0.03, right=0.95, top=0.95,
                         wspace=0.1, hspace=0.02)
        
    lons = 106
    lone = 164
    late = 49
    lats = 16
        
    ax_l_ = [ ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8 ]

    ax_l = []
    for i, ax in enumerate( ax_l_ ):
        
       stime = stime_l[i]
       print( i, stime, vtime)

       delta = (vtime - stime).total_seconds()
       if delta < 0:
          ax.axis('off')
          continue
       else:
          ax_l.append( ax )


    m_l = prep_proj_multi('merc', ax_l, fs=6,
                           ll_lon=lons, ur_lon=lone, ll_lat=lats, ur_lat=late )
 
    var_ = get_pw( INFO, stime=datetime( 2018, 7, 1, 0 ), vtime=vtime, m=0, )

    x2d, y2d = m_l[0](lon2d, lat2d)
        
    extend = 'max'

    unit = ""
    if nvar == "PW":
       levs = np.arange( 0, 17, 1)
    elif nvar == "MSLP":
       levs = np.arange( 0, 14, 1)
    elif nvar == "Z":
       levs = np.arange( 0, 85, 5 )
    elif nvar == "U" or nvar == "V":
       levs = np.arange( 0, 17, 1)
    elif nvar == "RAIN":
       levs = np.arange( 0, 75, 5 )
       levs = np.arange( 0, 105, 5 )
       adt = timedelta( hours=24 )
       unit = "(mm/24h)"
    elif nvar == "T":
       levs = np.arange( 0, 9, 1 )
       levs = np.arange( 0.5, 4.25, 0.25 )
       levs = np.arange( 0.2, 3.2, 0.2 )
       unit = "(K)"
    elif nvar == "THE":
       levs = np.arange( 0, 9, 1 )
       unit = "(K)"
    elif nvar == "QV":
       levs = np.arange( 0, 3.25, 0.25 )
       unit = r'(g/m$^3$)'
       if hpa < 700:    
          levs = np.arange( 0, 2.1, 0.1 )
    elif nvar == "RH":
       levs = np.arange( 0, 30, 3 )
       unit = r'(%)'
    elif nvar == "THEG":
       levs = np.arange( 0.0, 1.05, 0.05 )
       unit = r'(10$^{{-1}}$K/km)'

    clevs = np.arange( 900, 1100, 4 )
    cmap = plt.cm.get_cmap("hot_r")
    lc='k'

    mmax = 50 
#    mmax = 5 # DEBUG
    evar = np.zeros( ( mmax, var_.shape[0], var_.shape[1] ) )
    eslp = np.zeros( ( mmax, var_.shape[0], var_.shape[1] ) )
    egph = np.zeros( ( mmax, var_.shape[0], var_.shape[1] ) )
 
    for i, ax in enumerate( ax_l):
        
       stime = stime_l[i]
       print( i, stime, vtime)

       for m in range( 0, mmax ):
           slp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.01 # hPa
           gph_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1,)
           if nvar == "PW":
              var_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.001 # mm/m2
           elif nvar == "MSLP":
              var_ = slp_
           elif nvar == "Z":
              var_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "U" or nvar == "V" or nvar == "T":
              var_ =  get_prsvar( INFO, nvar=nvar+"prs", stime=stime, 
                          vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "RAIN":
              var_ = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
           elif nvar == "THE":
              var_ = get_the( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "QV":
              dens_ =  get_prsvar( INFO, nvar="DENSprs", stime=stime, 
                          vtime=vtime, m=m+1, hpa=hpa )
              var_ =  get_prsvar( INFO, nvar=nvar+"prs", stime=stime, 
                          vtime=vtime, m=m+1, hpa=hpa ) * dens_ * 1.e3
           elif nvar == "RH":
              var_ = get_rh( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa ) * 1.e2
           elif nvar == "THEG":
              vx_, vy_ = get_the_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa ) 
              var_ = np.sqrt( np.square(vx_) + np.square(vy_) ) * 1.e4

           evar[m,:,:] = var_
           eslp[m,:,:] = slp_
           egph[m,:,:] = gph_
           if m % 5 == 0:
              print( m )

       var = np.std( evar, ddof=1, axis=0)

       SHADE = ax.contourf( x2d, y2d, var, 
                             levels=levs, cmap=cmap,
                             extend=extend )

       var2_ = np.mean( eslp, axis=0 )
       if nvar == "U" or nvar == "V" or nvar == "T" or nvar == "QV" or nvar == "RH":
          var2_ = np.mean( egph, axis=0 )
          clevs = np.arange( 0, 15000, 20 )
       CONT = ax.contour( x2d, y2d, var2_, 
                           colors=lc,
                           linewidths=0.25, levels=clevs )
       ax.clabel( CONT, fontsize=6, fmt='%.0f' )

       ptit = 'Ini: {0:}'.format( stime.strftime('%HUTC %m/%d') )
       ax.text( 0.5, 0.95, ptit,
                fontsize=9, transform=ax.transAxes,
                horizontalalignment='center', 
                verticalalignment='center',
                bbox = bbox)



    pos = ax8.get_position()
    cb_width = 0.01
    cb_height = pos.height*1.5
    ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
    cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs[::2])
    cb.ax.tick_params( labelsize=8 )
        
    ax8.text( 1.001, 1.61, unit,
             fontsize=8, transform=ax8.transAxes,
             horizontalalignment='left', 
             verticalalignment='bottom', )

    pnum_l = [ "(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)" ]
    for i, ax in enumerate( ax_l ):
       ax.text( 0.01, 0.99, pnum_l[i],
                fontsize=9, transform=ax.transAxes,
                ha='left', va='top', 
                bbox = bbox )


    tnvar2 = "MSLP"
    tnvar = nvar
    if nvar != "MSLP" and nvar != "PW" and nvar != "RAIN":
       tnvar = nvar + str(hpa)
 
    tnvar_ = tnvar
   
    if nvar == "THEG":
       tnvar = r'|$\nabla \theta_e$| @' + str(hpa) + 'hPa'
       tnvar_ = nvar + str(hpa)

    if nvar == "U" or nvar == "V" or nvar == "T" or nvar == "QV" or nvar == "RH":
       tnvar2 = "Z" + str(hpa)

    tit = '{0:} spread & {1:}, valid: {2:}'.format( tnvar, tnvar2, vtime.strftime('%HUTC %m/%d') )

    fig.suptitle( tit, fontsize=12 )
        
    opath = "png/sprd_multi"
    ofig = "sprd_{0:}_v{1:}".format( tnvar_, vtime.strftime('%H%m%d') ) 

    if not quick:

      os.makedirs(opath, exist_ok=True)
    
      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
    else:
      print(ofig)
      plt.show()



# forecast loop

stime_l = [ 
           # datetime( 2018, 6, 26, 0),
            datetime( 2018, 6, 27, 0),
            datetime( 2018, 6, 28, 0),
            datetime( 2018, 6, 29, 0),
            datetime( 2018, 6, 30, 0),
            datetime( 2018, 7,  1, 0),
            datetime( 2018, 7,  2, 0),
            datetime( 2018, 7,  3, 0),
            datetime( 2018, 7,  4, 0),
          ]

nvar = "PW"
nvar = "MSLP"
nvar = "Z"
nvar = "U"
nvar = "RAIN"
nvar = "T"
nvar = "THE"
nvar = "RH"
nvar = "T"
nvar = "QV"
#nvar = "V"
hpa = 950
hpa = 700
#hpa = 500
#hpa = 300

nvar_l = [ "QV", "U", "T", "RH", ]
hpa_l = [ 950, 700, 850, 300, 200 ]

nvar_l = [ "MSLP", ]
nvar_l = [ "RAIN", ]
hpa_l = [ 950,  ]

stime = datetime( 2018, 6, 27, 0 )
etime = datetime( 2018, 7, 6, 0 )
stime = etime

#stime = datetime( 2018, 7, 5, 0 )
#etime = datetime( 2018, 7, 5, 0 )

time = stime
while time <= etime:
   for hpa in hpa_l:
      for nvar in nvar_l:
          main( stime_l=stime_l, vtime=time, nvar=nvar, hpa=hpa )

   time += timedelta( days=1 )


