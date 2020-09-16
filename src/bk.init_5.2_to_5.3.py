import numpy as np
import os
import sys

from datetime import datetime
from netCDF4 import Dataset
#from scale.io import ScaleIO

#mems = list(range(1, 51))

time = datetime( 2018, 6, 24, 0, 0, 0 )

MEMBER = 1
mem_list = [str(x).zfill(4) for x in range(1,MEMBER+1)]
mem_list.append("mean")
mem_list.append("mdet")
print(mem_list)



# original
imax_o = 40
jmax_o = 40
px_o = 8
py_o = 6

# new
imax_n = 20
jmax_n = 20
px = 16
py = 12

ihalo = 2
jhalo = 2

nprc = 4 # debug
nprc = px*py 


org_dir = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/org/20180624000000/anal"
new_dir = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/new/20180624000000/anal"

base_dir = "/data_ballantine02/miyoshi-t/honda/SCALE-LETKF/BAIU2018_5.3.6/new/20180624000000/base"


org_vars = [ 'DENS', 'MOMZ', 'MOMX', 'MOMY', 'RHOT', 'QV', 'QC', 'QR', 'QI', 'QS', 'QG' ]
org_vars = [ 'DENS', ]



for mem in mem_list:

    new_ = os.path.join( new_dir, mem)
    os.makedirs( new_, exist_ok=True)
    print(new_)

    cstime = time.strftime('%Y%m%d-%H%M%S.000')

    for p in range(nprc):
       base_ = os.path.join( base_dir, "mean", 'init.d01_{0:}.pe{1:0=6}.nc'.format( cstime, p ) )
       new_ = os.path.join( new_dir, mem, 'init.pe{0:0=6}.nc'.format(p) )
 
       yrank = p//px + 1
       xrank = p - px*(yrank-1) + 1

       yrank_o = (yrank+1) // 2 
       xrank_o = (xrank+1) // 2 

       # global indices in new and org
       isg_n = imax_n*(xrank-1)
       ieg_n = isg_n + imax_n + ihalo*2

       isg_o = imax_o*(xrank_o-1) 
       ieg_o = isg_o + imax_o + ihalo*2

       jsg_n = jmax_n*(yrank-1)
       jeg_n = jsg_n + jmax_n + jhalo*2

       jsg_o = jmax_o*(yrank_o-1) 
       jeg_o = jsg_o + jmax_o + jhalo*2

       # local indices
       isl_o = isg_n - isg_o
       #iel_o = isl_o + imax_n + ihalo*2
       iel_o = isl_o + imax_n 
       if xrank == 1:
          iel_o += ihalo

       jsl_o = jsg_n - jsg_o
       #jel_o = jsl_o + jmax_n + jhalo*2
       jel_o = jsl_o + jmax_n 
       if yrank == 1:
          jel_o += jhalo

       p_org = (yrank_o-1) * px_o + xrank_o - 1
       print( 'Rank:{0:} (old:{1:}), I:{2:}-{3:}, J:{4:}-{5:}'.format( p, p_org, isl_o, iel_o, jsl_o, jel_o ) )
     
       org_ = os.path.join( org_dir, mem, 'init.pe{0:0=6}.nc'.format(p_org) )


       with Dataset( base_ ) as src, Dataset( new_, "w") as dst, Dataset( org_, "r") as org:
           # copy global attributes all at once via dictionary
           dst.setncatts(src.__dict__)

           # copy dimensions
           for name, dimension in src.dimensions.items():
               dst.createDimension(
                   name, (len(dimension) if not dimension.isunlimited() else None))

           ## original variables
           #org_vars = []
           #for name, variable in org.variables.items():
           #    org_vars.append( name )
           #print( org_vars )
           #sys.exit()

           # copy all file data
           for name, variable in src.variables.items():
               #print( name, variable.datatype, variable.dimensions  )

               x = dst.createVariable(name, variable.datatype, variable.dimensions)
               dst[name].setncatts(src[name].__dict__)
               dst[name][:] = src[name][:]
               # copy variable attributes all at once via dictionary
               if name in org_vars:
                  print( variable.dimensions )
                  print( "HIT", name, "org:",org[name][jsl_o:jel_o,isl_o:iel_o,:].shape, dst[name].shape)
                  dst[name][:] = org[name][jsl_o:jel_o,isl_o:iel_o,:]

#               if name != "MOMZ":
#                  x = dst.createVariable(name, variable.datatype, variable.dimensions)
#                  #dst[name][:] = src[name][:]

    sys.exit()

    if type(imem) == int:
        ibasename = basename.format('{:04d}'.format(imem))
    else:
        ibasename = basename.format(imem)
    print(ibasename)

    sio = ScaleIO(ibasename, mode='r+', cache=False, bufsize=0, verbose=1)

    dtype = sio.rootgrps[0].variables['DENS'].dtype
    dimensions = sio.rootgrps[0].variables['DENS'].dimensions
    endian = sio.rootgrps[0].variables['DENS'].endian()

    for ivar, attrs in new_vars1.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars2.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars3.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars4.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars5.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars6.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars7.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars8.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars9.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars10.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)

    for ivar, attrs in new_vars11.items():
        print(ivar)

        for ifr in sio.rootgrps:
            ifr.createVariable(ivar, dtype, dimensions=dimensions, endian=endian)
            ifr.variables[ivar][:] = 0.0
            for iattr, value in attrs.items():
                ifr.variables[ivar].setncattr(iattr, value)


    del sio

