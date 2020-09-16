from netCDF4 import Dataset
import numpy as np 

from tools_BAIU import prep_proj_multi

def main():

   anal = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/20180703000000/fcst_sno_np00001/mean/p_history.pe000000.nc"
   gues = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/20180703000000/fcst_sno_np00001/mean_gues/p_history.pe000000.nc"

   with Dataset( anal, "r", format="NETCDF4") as nc:
       olra = nc.variables["OLR"][0,:,:]
       #olra = nc.variables["Tprs"][0,2,:,:]

   with Dataset( gues, "r", format="NETCDF4") as nc:
       olrb = nc.variables["OLR"][0,:,:]
       lon = nc.variables["lon"][:]
       lat = nc.variables["lat"][:]
       #olrb = nc.variables["Tprs"][0,2,:,:]

   import matplotlib.pyplot as plt

   fig, ax1 = plt.subplots( 1, 1, figsize=( 6, 5.5 ) )
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
   levs = np.arange( -12, 14, 2 )

   var = olra - olrb
   print( np.max( olra ))
   print( np.max( olrb ))
   print( np.max( var ))

   print( lon.shape )
   SHADE = ax1.contourf( x2d, y2d, var, cmap=cmap, levels=levs,
                    extend='both' )
   cb = plt.colorbar( SHADE )
   plt.show()

main()

