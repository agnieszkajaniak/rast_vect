import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr, osr
import os
from scipy.spatial import distance as ssd
from scipy.spatial import distance_matrix

path = os.path.join(os.path.expanduser("~"), "Documents", "pg", "vector_bootcamp")
pointfile = os.path.join(path, "sklepy.shp")

class vect():
    def __init__(self, pointfile):
        self.vector = ogr.Open(pointfile, 0)
        self.layer = self.vector.GetLayer()
        self.ext = self.layer.GetExtent()
        self.nfeatures = self.layer.GetFeatureCount()
        self.projection = self.layer.GetSpatialRef()
        defn = self.layer.GetLayerDefn()
        nfields = defn.GetFieldCount()
        print self.layer.GetGeomType() == ogr.wkbPoint

        fnames = [defn.GetFieldDefn(i).GetName() for i in range(nfields)]
        types = [defn.GetFieldDefn(i).GetTypeName() for i in range(nfields)]
        self.fields = dict(zip(fnames, types))

        self.layer.ResetReading()
        attrs = []
        points = []
        for f in self.layer:  # f - feature
            attrs.append([f.GetField(i) for i in range(nfields)])
            points.append(f.GetGeometryRef().GetPoint())

        self.arr_points = np.array(points)
        self.arr_points = self.arr_points[:, 0:2]
        self.dm = distance_matrix(self.arr_points, self.arr_points)

        self.vector = None

    def createFile(self, type, filename, points_data=None, line_data=None, polygon_data=None):
        proj = osr.SpatialReference()
        proj.ImportFromEPSG(2180)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if (type == "point"):
            pointFile = driver.CreateDataSource(self.name)
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
            lineFile = driver.CreateDataSource(name)
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
            polyFile = driver.CreateDataSource(name)
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

    def copyFile(self, filename, mdd):
        src = ogr.Open(pointfile, 0)
        layer = src.GetLayerByIndex(0)
        driver = ogr.GetDriverByName('ESRI Shapefile')
        ds = driver.CreateDataSource(filename)
        dest_layer = ds.CreateLayer('layer1',
                                    srs=layer.GetSpatialRef(),
                                    geom_type=layer.GetLayerDefn().GetGeomType())
        feature = layer.GetFeature(0)
        [dest_layer.CreateField(feature.GetFieldDefnRef(i)) for i in range(feature.GetFieldCount())]


        medoid = ogr.FieldDefn("Medoid", ogr.OFTInteger)  # utworzenie nowej kolumny
        dest_layer.CreateField(medoid)

        for pt in self.arr_points:
            feature1 = ogr.Feature(dest_layer.GetLayerDefn())  # 1
            point = ogr.Geometry(ogr.wkbPoint)  # 2
            point.AddPoint(pt[0], pt[1])  # 2
            feature1.SetGeometry(point)  # 2
            dest_layer.CreateFeature(feature1)  # 4
            feature1 = None

        for i in range(len(dest_layer)):
            if i == mdd:
                feature = ogr.Feature(dest_layer.GetLayerDefn())
                feature.SetField("Medoid", 1)
                dest_layer.CreateFeature(feature)
            else:
                feature = ogr.Feature(dest_layer.GetLayerDefn())
                feature.SetField("Medoid", 0)
                dest_layer.CreateFeature(feature)
            feature = None


        pointFile = None

    def medoid(self, name):
        self.name = name
        med = np.argmin(self.dm.sum(axis=1))  # to find medoid ID
        self.copyFile(filename = self.name, mdd = med)



    def centeroid(self, name):
        self.name = name
        mean_x = np.mean(self.arr_points[:, 0])
        mean_y = np.mean(self.arr_points[:, 1])
        result = []
        temp = []
        temp.append(mean_x)
        temp.append(mean_y)
        result.append(temp)
        result = np.array(result)
        self.createFile(type='point', filename = self.name, points_data=result)


    def conhul(bufdist):
        pointfile = os.path.join(path, namefile)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        source = driver.Open(pointfile, 0)
        layer = source.GetLayer()
        geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        for ef in layer:
            geomcol.AddGeometry(ef.GetGeometryRef())
        hull = geomcol.ConvexHull()
        poly = hull.Buffer(bufdist)
        print "%s buffered by %d is %s" % (hull.ExportToWkt(), bufdist, poly.ExportToWkt())

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

    def summary(self):
        self.extent = "Extent:\t{0:s}\n".format(self.ext)
        self.project = "Projection:\t{0:s}\n".format(self.projection.ExportToMICoordSys())
        self.filed = "Fields:\t{0:s}\n".format(self.fields)
        self.nf = "Number of object:\t{0:n}\n".format(self.nfeatures)
        print(self.extent + self.project + self.filed + self.nf)

v = vect(pointfile)
