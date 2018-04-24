import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr
import os

path = os.path.join(os.path.expanduser("~"), "Documents", "pg", "wektor")

we = 10000
sn = 12000
w = 483000
s = 623000
numpoints = 150


def random_points(w, s, we, sn, numpoints):
    points = np.random.power(5, (numpoints, 2))
    points[:, 0] = points[:, 0] * we + w
    points[:, 1] = points[:, 1] * sn + s
    return points


points = random_points(w, s, we, sn, 150)
print (points[0:10, :])

from osgeo import osr

proj = osr.SpatialReference()
proj.ImportFromEPSG(2180)
driver = ogr.GetDriverByName("ESRI Shapefile")

pointFile = driver.CreateDataSource("punkty.shp")
pointLayer = pointFile.CreateLayer("layer", proj, ogr.wkbPoint)

fieldDef = ogr.FieldDefn("ID", ogr.OFTInteger)  # ogr.OFT... String, Binary, Real, Date, Datetime, Binary, WideString
pointLayer.CreateField(fieldDef)

ID = 1
for pt in points:
    feature = ogr.Feature(pointLayer.GetLayerDefn())  # 1
    point = ogr.Geometry(ogr.wkbPoint)  # 2
    point.AddPoint(pt[0], pt[1])  # 2
    feature.SetGeometry(point)  # 2
    feature.SetField("ID", ID)  # 3
    pointLayer.CreateFeature(feature)  # 4
    feature = None
    ID += 1

pointFile = None

mean_x = np.mean(points[:, 0])
mean_y = np.mean(points[:, 1])
p_mean = [mean_x, mean_y]
print(mean_x, mean_y)


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# def funkcja(p):
#     return distance(p_mean, p)
dists = map(lambda p: distance(p_mean, p), points)
r = np.std(dists)
print r


def circle(center, radius):
    x, y = center
    angles = np.linspace(0, 2 * np.pi, 32)
    points1 = np.sin(angles) * radius + y
    points2 = np.cos(angles) * radius + x
    points = np.stack((points2, points1), axis=-1)
    return points

c = circle(p_mean, r)



polyFile = driver.CreateDataSource("poligon.shp")
polyLayer = polyFile.CreateLayer("layer", proj,ogr.wkbPolygon)
# Name: string
polyDef = ogr.FieldDefn("Name", ogr.OFTString)
polyDef.SetWidth(50) # setWidth dla tekstu
polyLayer.CreateField(fieldDef)
# area: real
fieldDef = ogr.FieldDefn("Area", ogr.OFTReal)
polyLayer.CreateField(fieldDef)

ring_geom=ogr.Geometry(ogr.wkbLinearRing)

for row in c:
    ring_geom.AddPoint(*tuple(row))


polygon = ogr.Geometry(ogr.wkbPolygon)
polygon.AddGeometry(ring_geom)
print(polygon.Area())



feature = ogr.Feature(polyLayer.GetLayerDefn())
feature.SetGeometry(polygon)
# feature.SetField("Name", "poly")
feature.SetField("Area", polygon.Area())
polyLayer.CreateFeature(feature)
feature.Destroy()


polyFile = None

minmax = []
minmax.append([np.argmin(points[:,0]), np.argmax(points[:,0])])
minmax.append([np.argmin(points[:,1]), np.argmax(points[:,1])])


lineFile = driver.CreateDataSource("linie.shp")
lineLayer = lineFile.CreateLayer("layer", proj,ogr.wkbLineString)
fieldDef = ogr.FieldDefn("ID", ogr.OFTInteger)
lineLayer.CreateField(fieldDef)


for ID, row in enumerate(minmax):
    feature = ogr.Feature(lineLayer.GetLayerDefn())
    line = ogr.Geometry(ogr.wkbLineString)

    for index in row:
        point = points[index]
        line.AddPoint(float(point[0]), float(point[1]))

    feature.SetGeometry(line)
    feature.SetField("ID", int(ID))
    lineLayer.CreateFeature(feature)
    feature = None

lineFile = None

