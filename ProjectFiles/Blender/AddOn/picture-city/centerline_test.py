from shapely.geometry import Polygon
from centerline.geometry import Centerline

polygon = Polygon([[0, 0], [0, 4], [4, 4], [4, 0]])
attributes = {"id": 1, "name": "polygon", "valid": True}

centerline = Centerline(polygon, **attributes)

print(centerline.geometry.geoms)
for linestring in centerline.geometry.geoms:
    print("linestart")
    for co in linestring.coords:
        print("point: " + str(co[0]) + " " + str(co[1]))

    print("lineend")