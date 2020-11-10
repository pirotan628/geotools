from pygc import *
import pgeotools as pg
from pg_param import *

lon0, lat0 = 134.9953139534642, 34.31518290300008  # South Center

azm, dist, itr = 90, -0.1 * NMILE, 30

#print("{0} {1}".format(lon0,lat0))
xyarray = pg.make_regular_interval(lon0, lat0, azm, dist, itr)
for i in range(len(xyarray)):
    lon, lat = xyarray[i][0], xyarray[i][1]
    print("{0} {1}".format(lon, lat))