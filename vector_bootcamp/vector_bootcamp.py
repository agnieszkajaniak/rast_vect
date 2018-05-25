import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr
import os
from scipy.spatial import distance as ssd
from scipy.spatial import distance_matrix




def createFile(type, points_data=None, line_data=None, polygon_data=None):
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
        for i in range(len(line_data)):
            feature = ogr.Feature(lineLayer.GetLayerDefn())
            line = ogr.Geometry(ogr.wkbLineString)
            lineDef = line_data
        for row in lineDef:
            line.AddPoint((row[0]), (row[1]))
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
        feature.SetGeometry(polygon)
        feature.SetField("Name", "poly")
        polyLayer.CreateFeature(feature)
        feature.Destroy()
        polyFile = None

def clique(self, dist_matrix):
    nrow, ncol = dist_matrix.shape
    triu = np.triu(dist_matrix)
    vals = ssd.squareform(triu)
    ind = np.triu_indices(nrow, 1)
    sel = vals < prog
    tab = (ind[0][sel],ind[1][sel],vals[sel])




createFile("polygon", polygon_data=points)
os.chdir(path)

########
from scipy.spatial.distance import squareform

ind = np.triu_indices(3, 1)
vals = squareform(macierz)
sel = vals < prog
ind[0][sel]

lista = zip(ind[0][sel], ind[1][sel], vals[sel])