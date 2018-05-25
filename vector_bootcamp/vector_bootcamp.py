import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr, osr
import os
from scipy.spatial import distance as ssd
from scipy.spatial import distance_matrix

path = os.path.join(os.path.expanduser("~"), "Documents", "pg", "vector_bootcamp")
pointfile = os.path.join(path, "punkty.shp")

class vect():
    def __init__(self, pointfile):
        vector = ogr.Open(pointfile, 0)
        layer = vector.GetLayer()
        nfeatures = layer.GetFeatureCount()
        projection = layer.GetSpatialRef()
        defn = layer.GetLayerDefn()
        nfields = defn.GetFieldCount()

        fnames = [defn.GetFieldDefn(i).GetName() for i in range(nfields)]
        types = [defn.GetFieldDefn(i).GetTypeName() for i in range(nfields)]
        fields = dict(zip(fnames, types))
        fields  # w formie dict

        layer.ResetReading()
        attrs = []
        points = []
        for f in layer:  # f - feature
            attrs.append([f.GetField(i) for i in range(nfields)])
            points.append(f.GetGeometryRef().GetPoint())

        self.arr_points = np.array(points)
        self.arr_points = self.arr_points[:, 0:2]
        self.dm = distance_matrix(self.arr_points, self.arr_points)

    def createFile(self, type, points_data=None, line_data=None, polygon_data=None):
        proj = osr.SpatialReference()
        proj.ImportFromEPSG(2180)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if (type == "point"):
            pointFile = driver.CreateDataSource("punkty.shp")
            pointLayer = pointFile.CreateLayer("layer", proj, ogr.wkbPoint)
            fieldDef = ogr.FieldDefn("ID", ogr.OFTInteger)
            pointLayer.CreateField(fieldDef)
            ID = 1
            for pt in points_data:
                feature = ogr.Feature(pointLayer.GetLayerDefn())
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(pt[0], pt[1])
                feature.SetGeometry(point)
                feature.SetField("ID", ID)
                pointLayer.CreateFeature(feature)
                feature = None
                ID += 1
            pointFile = None
        elif (type == "line"):
            lineFile = driver.CreateDataSource("linie.shp")
            lineLayer = lineFile.CreateLayer("layer", proj, ogr.wkbLineString)
            for row in line_data:
                feature = ogr.Feature(lineLayer.GetLayerDefn())
                line = ogr.Geometry(ogr.wkbLineString)
                line.AddPoint((row[0][0]), (row[0][1]))
                line.AddPoint((row[1][0]), (row[1][1]))
                feature.SetGeometry(line)
                lineLayer.CreateFeature(feature)
                feature = None

        elif (type == "polygon"):
            polyFile = driver.CreateDataSource("poligon.shp")
            polyLayer = polyFile.CreateLayer("layer", proj, ogr.wkbPolygon)
            polyDef = ogr.FieldDefn("Name", ogr.OFTString)
            polyDef.SetWidth(50)
            polyLayer.CreateField(polyDef)
            poligon = ogr.Geometry(ogr.wkbLinearRing)
            for row in polygon_data:
                poligon.AddPoint(*tuple(row))
            polygon = ogr.Geometry(ogr.wkbPolygon)
            polygon.AddGeometry(poligon)
            feature = ogr.Feature(polyLayer.GetLayerDefn())
            ind = np.triu_indices(nrow, 1)
            feature.SetGeometry(polygon)
            feature.SetField("Name", "poly")
            polyLayer.CreateFeature(feature)
            feature.Destroy()
            polyFile = None

    def clique(self, dist_matrix):
        triu = np.triu(dist_matrix)
        selected = np.argwhere(np.logical_and(triu < 800, triu > 0))
        result = []
        for (x, y) in selected:
            temp = []
            temp.append(self.arr_points[x])
            temp.append(self.arr_points[y])
            result.append(temp)
        result = np.array(result)
        self.createFile(type='line', line_data=result)

v = vect(pointfile)
x = v.clique(v.dm)