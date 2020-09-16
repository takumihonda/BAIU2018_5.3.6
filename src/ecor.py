import numpy as np

from netCDF4 import Dataset
from datetime import datetime
from datetime import timedelta
import os
import sys

import matplotlib.pyplot as plt
 
from tools_BAIU import get_lonlat, get_arain, get_pw, prep_proj_multi, draw_rec, get_gph, get_prsvar, get_the, get_the_grad, get_rh, get_mslp, get_mf_grad, get_q1, read_etrack, get_olr

quick = True   
#quick = False


def main( stime=datetime( 2018, 6, 30, 0), 
          slon=130.0, elon=137.5,
          slat=33.0, elat=36.0,
          adt_h=24,
          vtime_ref=datetime( 2018, 7, 6, 0, 0, 0 ),
          vtime_l=[], rvar="PW", tvar="PW", hpa=500 ):


    thrs = 100.0
    #thrs = 10.0
    thrs = 50.0

    TOP = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6"
    
    


    adt = timedelta( hours=adt_h )
    

    INFO = {"TOP": TOP, }



#    opath = "dat/ts_s" + stime.strftime('%H%m%d')
#    os.makedirs(opath, exist_ok=True)
#
#    of = 'v{0:}_thrs{1:03}mm_lon{2:04}_{3:04}_lat{4:04}_{5:04}.npz'.format( vtime_ref.strftime('%H%m%d'), thrs , slon, elon, slat, elat )
#    print( of )
#
#    data = np.load( os.path.join( opath, of) )
#
#    ts_l = data['ts']   
#    mem_l = data['mem']   
#
#    print( mem_l )
#    print( np.max(mem_l), np.min(mem_l) )
#    print( len(mem_l) )

    lon2d, lat2d = get_lonlat( INFO, stime=stime )




    pw_l = np.zeros( 50 )
    rain_l = np.zeros( 50 )


    # get reference
    for m in range( 50 ):
        rain_ = get_arain( INFO, stime=stime, vtime=vtime_ref, adt=adt, m=m+1 )
        rain_l[m] = np.mean( rain_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )

        pw_ = get_pw( INFO, stime=stime, vtime=vtime_ref, m=m+1, )
        pw_l[m] = np.mean( pw_[ (lon2d >= slon ) & (lon2d <= elon) & (lat2d >= slat) & (lat2d <= elat) ] )

    pw_l -= np.mean( pw_l )
    rain_l -= np.mean( rain_l )


    tclon_l, tclat_l, tcmslp_l, time_l = read_etrack( stime=stime, )
    tclon_l -= np.nanmean( tclon_l, axis=0, keepdims=True )
    tclat_l -= np.nanmean( tclat_l, axis=0, keepdims=True  )
    tcmslp_l -= np.nanmean( tcmslp_l, axis=0, keepdims=True  )

    print( "Reference read: complete" )

    bbox = {'facecolor':'w', 'alpha':0.8, 'pad':2}

    if rvar == "PW":
       ref_l = pw_l
    elif rvar == "RAIN":
       ref_l = rain_l
    elif rvar == "TCLON":
       ref_l = tclon_l[:,-1]
    print( ref_l )
    print( "" )

    lons = 105
    lone = 165
    late = 50
    lats = 15


    ecor = np.zeros( ( lon2d.shape[0], lon2d.shape[1] ) )

    evar = np.zeros( ( 50, lon2d.shape[0], lon2d.shape[1] ) )
    evar2 = np.zeros( ( 50, lon2d.shape[0], lon2d.shape[1] ) )

    for vtime in vtime_l:
       delta = (vtime - stime).total_seconds()   

       if delta < 0:
          continue

       fig, ( (ax1) ) = plt.subplots( 1, 1, figsize=( 8, 6 ) )
       fig.subplots_adjust( left=0.1, bottom=0.1, right=0.9, top=0.93,
                            wspace=0.1, hspace=0.02)
   
       ax_l = [ ax1 ]
       m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
               ll_lat=lats, ur_lat=late )
       x2d, y2d = m_l[0](lon2d, lat2d)


       for m in range( 50 ):
           gph_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           slp_ = get_mslp( INFO, stime=stime, vtime=vtime, m=m+1, )
           var2_ = gph_

           if tvar == "PW":
              var_ = get_pw( INFO, stime=stime, vtime=vtime, m=m+1, )
              var2_ = slp_

           elif tvar == "MSLP":
              var_ = slp_
              var2_ = var_
           elif tvar == "Z":
              var_ = get_gph( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "RAIN":
              var_ = get_arain( INFO, stime=stime, vtime=vtime, adt=adt, m=m+1 )
              var2_ = slp_
           elif tvar == "THE":
              var_ = get_the( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "THEY" or tvar == "THEX" or tvar == "THEYA":
              var_x, var_y = get_the_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if tvar == "THEY":
                 var_ = var_y
              elif tvar == "THEX":
                 var_ = var_x
              elif tvar == "THEYA":
                 var_ = np.abs( var_y )
           elif tvar == "RH":
              var_ = get_rh( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           elif tvar == "MFY" or tvar == "MFX":
              q_ = get_prsvar( INFO, nvar="QVprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              if tvar == "MFY":
                v_ = get_prsvar( INFO, nvar="Vprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              elif tvar == "MFX":
                v_ = get_prsvar( INFO, nvar="Uprs", stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              var_ = q_ * v_

           elif tvar == "MFD":
              var_ = get_mf_grad( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )

           elif tvar == "UDIF" or tvar == "VDIF":
              if tvar == "UDIF":
                 tvar_ = "Uprs"
              var1_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
              var2_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=950 )
              var_ = var1_ - var2_
           elif tvar == "Q1":
              var_ = get_q1( INFO, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
#              var2_ = get_q1( INFO, stime=stime, vtime=vtime, m=m+1, hpa=850 )
#              var_ -= var2_
           elif tvar == "OLR":
              var_ = get_olr( INFO, stime=stime, vtime=vtime, m=m+1, )
           else:
              tvar_ = tvar + "prs"
              var_ = get_prsvar( INFO, nvar=tvar_, stime=stime, vtime=vtime, m=m+1, hpa=hpa )
           evar[m,:,:] = var_[:]
           evar2[m,:,:] = var2_[:]
   
       evar -= np.mean( evar, axis=0 )
   
       cnt = 0
       ecor[:] = 0.0
       for m in range( 50 ):
           if np.isnan( ref_l[m] ):
              evar[m,:,:] = np.nan
              continue
           cnt += 1
           ecor += evar[m,:,:] * ref_l[m] 
   
       ecor = ecor / np.nanstd( ref_l, ddof=1 ) / np.nanstd( evar, ddof=1, axis=0 ) / cnt
       print("Count:",cnt)
       #ecor = var_ # DEBUG 
  
       print( np.nanmax( var_), np.nanmin(var_) )
       print( "Compute correlation" )

       levs = np.arange( -0.7, 0.8, 0.1 )
       cmap = plt.cm.get_cmap("RdBu_r")
   
       print( np.max(ecor), np.min(ecor) )
       SHADE = ax1.contourf( x2d, y2d, ecor, levels=levs,
                         cmap=cmap, extend='both' )
   
       pos = ax1.get_position()
       cb_width = 0.015
       cb_height = pos.height*0.98
       ax_cb = fig.add_axes( [pos.x1+0.01, pos.y0+0.01, cb_width, cb_height] )
       cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs)
       cb.ax.tick_params( labelsize=8 )

       draw_rec( m_l[0], ax1, slon, elon, slat, elat, lw=2.0, )

       lc = 'k'
       lw = 1.0
       if tvar == "MSLP" or tvar == "RAIN" or tvar == "PW":
          clevs = np.arange( 900, 1200, 4 )
          fac = 1.e-2
       else:
          clevs = np.arange( 0, 15000, 20 )
          fac = 1.0
          lw = 0.5
       CONT = ax1.contour( x2d, y2d, np.mean( evar2, axis=0 )*fac, 
                           colors=lc,
                           linewidths=lw, levels=clevs )
       ax1.clabel( CONT, fontsize=6, fmt='%.0f' )
  

       if rvar == "PW" or rvar == "RAIN":
          rrvar = rvar
       else:
          rrvar = rvar + str( hpa )

       if tvar == "PW" or tvar == "RAIN" or tvar == "MSLP" or tvar == "OLR":
          ttvar = tvar
       else:
          ttvar = tvar + str( hpa )


       tit = "Ensemble-based correlations: {0:} & {1:}".format( rrvar, ttvar )
       ofig = "ecor_r{0:}_t{1:}_v{2:}_vr{3:}_adt{4:0=3}".format( rrvar, ttvar, vtime.strftime('%H%m%d'), vtime_ref.strftime('%H%m%d'), adt_h ) 


       ax1.text( 0.5, 1.05, tit,
                fontsize=14, transform=ax1.transAxes,
                horizontalalignment='center', 
                verticalalignment='center', )

       if rvar == "RAIN":
          dt = ( vtime - ( vtime_ref - adt ) ).total_seconds() / 3600.0
       else:
          dt = ( vtime - ( vtime_ref ) ).total_seconds() / 3600.0
       note = "Valid: {0:}\nInit: {1:}\nT{2:0=+2}h".format( vtime.strftime('%HUTC %m/%d'), stime.strftime('%H UTC %m/%d'), int( dt ) )
       ax1.text( 0.99, 0.99, note,
                fontsize=12, transform=ax1.transAxes,
                horizontalalignment='right', 
                verticalalignment='top', 
                bbox=bbox, )
   
   
       print( ofig )
       
       if not quick:       
          opath = "png/ecor_s{0:}".format( stime.strftime('%H%m%d'),)
          os.makedirs(opath, exist_ok=True)
        
          ofig = os.path.join(opath, ofig + ".png")
          plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
          plt.clf()
       else:
          plt.show()
   



###################

stime = datetime( 2018, 6, 28, 0)
#stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 6, 30, 0)
#stime = datetime( 2018, 6, 26, 0)
#stime = datetime( 2018, 6, 27, 0)
#stime = datetime( 2018, 6, 29, 0)
stime = datetime( 2018, 7, 1, 0)
#stime = datetime( 2018, 7, 2, 0)
#stime = datetime( 2018, 7, 3, 0)


vtime_l = [ datetime( 2018, 7, 6, 0),
            datetime( 2018, 7, 4, 12), datetime( 2018, 7, 3, 12 ), 
            datetime( 2018, 7, 5, 0), datetime( 2018, 7, 4, 0 ),
            datetime( 2018, 7, 3, 0), datetime( 2018, 7, 2, 0 ), 
            datetime( 2018, 7, 1, 0), ]



vtime = datetime( 2018, 7, 5, 0 ), 

stime_l = [ datetime( 2018, 6, 28, 0), datetime( 2018, 6, 29, 0), 
            datetime( 2018, 6, 30, 0), datetime( 2018, 7,  1, 0), 
            datetime( 2018, 7,  2, 0), datetime( 2018, 7,  3, 0), 
          ]

stime_l = [ datetime( 2018, 7, 1, 0), datetime( 2018, 7, 2, 0) ]
stime_l = [ datetime( 2018, 7, 1, 0), ]
stime_l = [ datetime( 2018, 7, 2, 0), ]

stime_l = [ datetime( 2018, 7, 3, 0), ]

rvar = "PW"
rvar = "RAIN"

tvar = "PW"
#tvar = "Z"
#tvar = "V"

hpa = 300
hpa = 500
hpa = 850
hpa = 950

#tvar_l = [ "RAIN", "PW", "Z", "U", "V" ]
tvar_l = [ "T", "QV", ]
tvar_l = [ "T", "QV", "RAIN", "PW", "Z", "U", "V", "THE" ]
hpa_l = [ 200, 300, 500, 850, 950 ]

tvar_l = [ "MFY", ]
hpa_l = [ 850, 950 ]

#tvar_l = [ "PW"]
#tvar_l = [ "V"]
#tvar_l = [ "MSLP"]
#hpa_l = [ 700 ]

slon = 130.0
elon = 137.5
slat = 33.0 
elat = 36.0
#slon = 125.0
#elon = 135.0
#slat = 20.0
#elat = 35.0

vtime_ref = datetime( 2018, 7, 6, 0, 0 )
adt_h = 24

vtime_ref = datetime( 2018, 7, 7, 0, 0 )
adt_h = 48

vtime_l = [ 
            datetime( 2018, 7, 7, 0), datetime( 2018, 7, 6, 0 ),
            datetime( 2018, 7, 5, 0), datetime( 2018, 7, 4, 0 ),
            datetime( 2018, 7, 3, 0), datetime( 2018, 7, 2, 0 ), 
            datetime( 2018, 7, 1, 0), 
          ]

vtime_l = [ 
            datetime( 2018, 7, 5, 0), datetime( 2018, 7, 4, 0 ),
            datetime( 2018, 7, 3, 0), datetime( 2018, 7, 6, 0 ), 
            datetime( 2018, 7, 7, 0),
          ]


tvar_l = [ "OLR", ]
tvar_l = [ "Q1", ]
hpa_l = [ 500, ]

#vtime_l = [ datetime( 2018, 7, 5, 12), datetime( 2018, 7, 4, 12), datetime( 2018, 7, 3, 12) ]

#vtime_l = [ datetime( 2018, 7, 4, 12), datetime( 2018, 7, 4, 0), datetime( 2018, 7, 5, 0 ) ]


for stime in stime_l:

    for tvar in tvar_l:
    
        for hpa in hpa_l:
           main( stime=stime, vtime_l=vtime_l,   
                 slon=slon, elon=elon,
                 slat=slat, elat=elat,
                 vtime_ref=vtime_ref,
                 adt_h=adt_h,
                 rvar=rvar, tvar=tvar, hpa=hpa )
           if tvar == "PW" or tvar == "RAIN" or tvar == "UDIF" or tvar == "MSLP":
              break
