import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
 
from tools_BAIU import get_lonlat, prep_proj_multi, get_arain, get_mslp, get_pw, get_gph, get_prsvar, get_the, get_the_grad, get_rh, get_ki, get_hdiv_curl, get_the_grad


quick = True   
quick = False


def main( stime_l=[],
          vtime=datetime( 2018, 7, 5, 0 ), nvar="PW", hpa=500 ):

    adt = timedelta( hours=24 )


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

    cmap = plt.cm.get_cmap("hot_r")

    lc = 'k'
    lw = 0.5

    fac = 1.0
    unit = ""
    if nvar == "PW":
       levs = np.arange( 0, 72.5, 2.5)
       cmap = plt.cm.get_cmap("Blues")
       unit = r'(mm m$^{-2}$)'
       lc = 'gainsboro'
       lw = 1.0
    elif nvar == "MSLP":
       levs = np.arange( 0, 14, 1)
    elif nvar == "Z":
       levs = np.arange( 0, 85, 5 )
       levs = np.arange( 0, 13000, 20 )
       lw = 0.0
    elif nvar == "U":
       levs = np.arange( -50, 55, 5 )
       cmap = plt.cm.get_cmap("RdBu_r")
       extend = 'both'
    elif nvar == "V":
       levs = np.arange( 0, 17, 1)
       extend = 'both'
    elif nvar == "RAIN":
       cmap = plt.cm.get_cmap("jet")
       levs = np.arange( 10, 155, 5 )
       unit = "(mm/24h)"
    elif nvar == "THE":
       levs = np.arange( 280, 340, 2)
       unit = "(K)"
       cmap = plt.cm.get_cmap("jet")
    elif nvar == "THEY" or nvar == "THEX":
       cmap = plt.cm.get_cmap("RdBu_r")
       levs = np.arange( -1, 1.05, 0.05 )
       unit = r'(K/m$^4$)'
       fac = 1.e4
       extend = 'both'
    elif nvar == "THEYA":
       cmap = plt.cm.get_cmap("hot_r")
       levs = np.arange( 0.1, 2.1, 0.1 )
       unit = r'(K/m$^4$)'
       extend = 'max'
       fac = 1.e4

    elif nvar == "THEG":
       cmap = plt.cm.get_cmap("hot_r")
       levs = np.arange( 0.0, 1.05, 0.05 )
       unit = r'(10$^{{-1}}$K/km)'
       extend = 'max'
       fac = 1.e4

    elif nvar == "QV":
       cmap = plt.cm.get_cmap("BrBG")
       levs = np.arange( 0, 19.0, 1 )
       if hpa < 850:
          levs = np.arange( 0, 8.0, 0.5 )
       unit = r'(g/m$^3$)'
       fac = 1.e3
       extend = 'max'
 
    elif nvar == "RH":
       cmap = plt.cm.get_cmap("BrBG")
       levs = np.arange( 0, 100, 5 )
       fac = 1.e2
       extend = 'max'
   
    elif nvar == "KI":
       cmap = plt.cm.get_cmap("RdBu_r")
       cmap = plt.cm.get_cmap("RdPu")
       cmap = plt.cm.get_cmap("jet")
       levs = np.arange( 20, 46, 1 )
       levs = np.arange( 10, 41, 1 )
       fac = 1.0
       extend = 'both'

    elif nvar == "DIV":
       levs = np.arange( -3, 3.2, 0.2 )
       cmap = plt.cm.get_cmap("RdBu_r")
       fac = 1.e5
       unit = r'(10$^{-5}$s$^{-1}$)'
       extend = 'both'

    clevs = np.arange( 900, 1100, 4 )

    mmax = 50 
#    mmax = 5 # DEBUG
    evar = np.zeros( ( mmax, var_.shape[0], var_.shape[1] ) )
    eslp = np.zeros( ( mmax, var_.shape[0], var_.shape[1] ) )
 
    for i, ax in enumerate( ax_l):
        
       stime = stime_l[i]
       print( i, stime, vtime)

       for m in range( 0, mmax ):
           slp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.01 # hPa
           if nvar == "PW":
              var_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1,) * 0.001 # mm/m2
           elif nvar == "MSLP":
              var_ = slp_
           elif nvar == "Z":
              var_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "U" or nvar == "V":
              var_ =  get_prsvar( INFO, nvar=nvar+"prs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )

           elif nvar == "DIV" or nvar == "CURL":
              div_, curl_ =  get_hdiv_curl( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if nvar == "DIV":
                  var_ = div_
              elif nvar == "CURL":
                  var_ = curl_

           elif nvar == "QV":
              
              dens_ =  get_prsvar( INFO, nvar="DENSprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              var_ =  get_prsvar( INFO, nvar=nvar+"prs", stime=stime, vtime=vtime, m=m+1, hpa=hpa ) * dens_
           elif nvar == "RAIN":
              var_ =  get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
           elif nvar == "THE":
              var_ = get_the( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "THEY" or nvar == "THEX" or nvar == "THEYA":
              var_x, var_y = get_the_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if nvar == "THEY":
                 var_ = var_y
              elif nvar == "THEX":
                 var_ = var_x
              elif nvar == "THEYA":
                 var_ = np.abs( var_y )

           elif nvar == "RH":
              var_ = get_rh( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif nvar == "KI":
              var_ = get_ki( INFO, stime=stime, vtime=vtime, m=m+1 )

           elif nvar == "THEG":
              vx_, vy_ = get_the_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa ) 
              var_ = np.sqrt( np.square(vx_) + np.square(vy_) ) 

           evar[m,:,:] = var_
           eslp[m,:,:] = slp_
           if m % 5 == 0:
              print( m )

       var = np.nanmax( evar, axis=0) * fac
       print( '{0:}, max:{1:.2f}, min:{2:.2f}'.format( nvar, np.nanmax(var), np.nanmin(var) ) )

       if nvar != "Z":
          SHADE = ax.contourf( x2d, y2d, var, 
                                levels=levs, cmap=cmap,
                                extend=extend )
          slp_ = np.mean( eslp, axis=0 )
          CONT = ax.contour( x2d, y2d, slp_, 
                              colors=lc,
                              linewidths=lw, levels=clevs )
          ax.clabel( CONT, fontsize=6, fmt='%.0f' )


       else:
          CONT0 = ax.contour( x2d, y2d, var, 
                             levels=levs, colors='k',
                             linewidths=0.2 )
          ax.clabel( CONT0, fontsize=6, fmt='%.0f' )

       ptit = 'Ini: {0:}'.format( stime.strftime('%HUTC %m/%d') )
       ax.text( 0.5, 0.95, ptit,
                fontsize=9, transform=ax.transAxes,
                horizontalalignment='center', 
                verticalalignment='center',
                bbox = bbox)

       if nvar == "PW":
          CONT0 = ax.contour( x2d, y2d, var, 
                              colors='aqua', linestyles='solid',
                              linewidths=1.0, levels=[60,] )
          ax.clabel( CONT0, fontsize=8, fmt='%.0f' )
   

    if nvar != "Z":
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

        

    tnvar = nvar
    tnvar_ = nvar
    if nvar != "MSLP" and nvar != "PW" and nvar != "RAIN":
       tnvar_ = nvar + str(hpa)
       tnvar = tnvar_

    if nvar == "THEY":
       tnvar = r'$\partial \theta_e/\partial y$ @' + str(hpa) + 'hPa'
    elif nvar == "THEX":
       tnvar = r'$\partial \theta_e/\partial x$ @' + str(hpa) + 'hPa'
    elif nvar == "THEYA":
       tnvar = r'|$\partial \theta_e/\partial y$| @' + str(hpa) + 'hPa'
    elif nvar == "THE":
       tnvar = r'$\theta_e$ @' + str(hpa) + 'hPa'
    elif nvar == "KI":
       tnvar = 'K index'
       tnvar_ = "KI"
    elif nvar == "THEG":
       tnvar = r'|$\nabla \theta_e$| @' + str(hpa) + 'hPa'

    if nvar == "Z":
       tit = '{0:}, valid: {1:}'.format( tnvar, vtime.strftime('%HUTC %m/%d') )
    else:
       tit = '{0:} & MSLP, valid: {1:}'.format( tnvar, vtime.strftime('%HUTC %m/%d') )

    fig.suptitle( tit, fontsize=12 )
        
    opath = "png/max_multi"
    ofig = "max_{0:}_v{1:}".format( tnvar_, vtime.strftime('%H%m%d') ) 

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

stime_l = [ datetime( 2018, 6, 26, 0),
            datetime( 2018, 6, 27, 0),
            datetime( 2018, 6, 28, 0),
            datetime( 2018, 6, 29, 0),
            datetime( 2018, 6, 30, 0),
            datetime( 2018, 7,  1, 0),
            datetime( 2018, 7,  2, 0),
            datetime( 2018, 7,  3, 0),
          ]

nvar = "PW"
#nvar = "MSLP"
nvar = "Z"
nvar = "U"
nvar = "V"
nvar = "THE"
nvar = "THEY"
#nvar = "THEX"
nvar = "THEYA"
nvar = "QV"
nvar = "RH"
nvar = "KI"
nvar = "DIV"
nvar = "THEG"
nvar = "RAIN"
hpa = 950
#hpa = 500
#hpa = 300
#hpa = 200

hpa_l = [ 950, 850, 700, 500, 300, 200 ]
hpa_l = [ 950 ]

stime = datetime( 2018, 6, 27, 0 )

etime = datetime( 2018, 7, 6, 0 )
time = stime
while time <= etime:
   for hpa in hpa_l:
       main( stime_l=stime_l, vtime=time, nvar=nvar, hpa=hpa )
       if nvar == "PW" or nvar == "MSLP" or nvar == "RAIN" or nvar == "KI":
          break
   time += timedelta( days=1 )


