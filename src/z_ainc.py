from netCDF4 import Dataset
import numpy as np 

import os
import sys
from datetime import datetime, timedelta

from tools_BAIU import prep_proj_multi

quick = True
quick = False

def main( time=datetime(2018, 7, 2, 0), hpa=500 ):

   ctime = time.strftime('%Y%m%d%H%M%S')

   anal = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/{0:}/fcst_sno_np00001/mean/p_history.pe000000.nc".format( ctime )
   gues = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/{0:}/fcst_sno_np00001/mean_gues/p_history.pe000000.nc".format( ctime )

   with Dataset( anal, "r", format="NETCDF4") as nc:
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()

       za = nc.variables["Gprs"][0,idx_v,:,:]

   with Dataset( gues, "r", format="NETCDF4") as nc:
       prs = nc.variables["pressure"][:] # hPa
       idx_v = np.abs( ( prs - hpa ) ).argmin()
       zb = nc.variables["Gprs"][0,idx_v,:,:]
       lon = nc.variables["lon"][:]
       lat = nc.variables["lat"][:]

   import matplotlib.pyplot as plt

   fig, ax1 = plt.subplots( 1, 1, figsize=( 8, 6.5 ) )
   fig.subplots_adjust( left=0.05, bottom=0.05, right=0.95, top=0.95,
                        wspace=0.1, hspace=0.3)

   lons = 105 + 6
   lone = 165 - 6
   late = 50
   lats = 16

   ax_l = [ ax1, ] # ax5, ax6 ]
   m_l = prep_proj_multi('merc', ax_l, ll_lon=lons, ur_lon=lone, 
                          ll_lat=lats, ur_lat=late, fs=6 )

   x2d, y2d = m_l[0](lon, lat)

   cmap = plt.cm.get_cmap("RdBu_r")
   levs = np.arange( -20, 22, 2 )

   var = za - zb
   print( np.max( var ))

   print( lon.shape )
   SHADE = ax1.contourf( x2d, y2d, var, cmap=cmap, levels=levs,
                    extend='both' )
   pos = ax1.get_position()
   cb_width = 0.015
   cb_height = pos.height*0.98
   ax_cb = fig.add_axes( [pos.x1, pos.y0+0.01, cb_width, cb_height] )
   cb = plt.colorbar( SHADE, cax=ax_cb, orientation = 'vertical', ticks=levs )
   cb.ax.tick_params( labelsize=8 )


   tit = "Z{0:0=3} analysis increment at {1:}".format( hpa, time.strftime('%HUTC %m/%d/%Y') )
   ax1.text( 0.5, 1.01, tit,
            fontsize=12, transform=ax1.transAxes,
            ha='center',
            va='bottom',
          )

   ofig = "1p_ainc_Z{0:0=3}_{1:}".format( hpa, time.strftime('%m%d%H') )
   if not quick:
      opath = "png/1p_z_ainc"
      os.makedirs( opath, exist_ok=True )

      ofig = os.path.join(opath, ofig + ".png")
      plt.savefig(ofig,bbox_inches="tight", pad_inches = 0.1)
      print(ofig)
      plt.clf()
   else:
      print(ofig)
      plt.show()

#######################

time = datetime( 2018, 7, 2, 12, 0 )
time = datetime( 2018, 7, 2, 6, 0 )
time = datetime( 2018, 7, 2, 18, 0 )
#time = datetime( 2018, 7, 3, 0, 0 )

stime = datetime( 2018, 7, 2, 0, 0 )
etime = datetime( 2018, 7, 3, 0, 0 )

#etime = stime

hpa = 850
hpa = 300

time = stime
while time <= etime:
  main( time=time, hpa=hpa )
  time += timedelta( hours=6 )
