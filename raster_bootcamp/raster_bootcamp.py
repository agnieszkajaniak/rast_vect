import os
from osgeo import gdal
from os.path import basename, splitext
import numpy as np

os.chdir(os.path.join(os.path.expanduser("~"), "Documents", "pg", "raster_bootcamp", "dist"))
lista = os.listdir(".")


class rast:
    def __init__(self, *lista):
        self.rasters = []
        self.metadata = []
        for r in lista:
            raster = gdal.Open(r)
            self.rasters.append(raster)
            if raster == None:
                raise Exception("To nie jest plik rastrowy /%s" % raster)
            self.metadata.append(self._getMetadata(raster))
        l = (len(self.metadata)) - 1
        for i in range(l):
            if self.metadata[0] != self.metadata[i+1]:
                raise Exception("Niezgodne rastry")
        self.names = self._getNames(*lista)
        self.result = np.zeros(self.size[0])
        self.result.shape = (1, self.size[0])
        self._summary()
        self._calculator

    def _getMetadata(self, raster):
        self.geoTransform = raster.GetGeoTransform()
        self.size = (raster.RasterXSize, raster.RasterYSize)
        self.projection = raster.GetProjection()
        self.resolution = (abs(self.geoTransform[1]), abs(self.geoTransform[5]))
        minX = self.geoTransform[0]
        maxY = self.geoTransform[3]
        maxX = minX + self.geoTransform[1] * self.size[0]
        minY = maxY + self.geoTransform[5] * self.size[1]
        self.extent = (minX, maxX, minY, maxY)
        return (self.size, self.projection, self.resolution, self.extent)

    def _getNames(self, *lista):
        return ([basename(splitext(raster)[0]) for raster in lista])

    def _getLines(self, row):
        self.__data = np.empty([len(self.rasters), self.size[0]])
        for i, ptr in enumerate(self.rasters):
            p = ptr.GetRasterBand(1).ReadAsArray(0, row, self.size[0], 1)
            self.__data[i] = p

    def _calc(self, expression):
        dct = dict(zip(self.names, self.__data))
        self.result[0] = eval(expression, dct)

    def _summary(self):
        name = "Name:{0:s}\n".format(self.names)
        size = "Size:{0:s}\n".format(self.size)
        proj = "Projection:{0:s}\n".format(self.projection)
        res = "Resolution:{0:s}\n".format(self.resolution)
        ext = "Extent:{0:s}\n".format(self.extent)
        print(name + size + proj + res + ext)

    def _calculator(self, expression):
        cols, rows = self.size
        driver = gdal.GetDriverByName("GTiff")
        target = driver.Create("../result.tif", cols, rows, 1, gdal.GDT_Float32)
        target.SetProjection(self.projection)
        target.SetGeoTransform(self.geoTransform)
        noData = -1
        tband = target.GetRasterBand(1)
        tband.SetNoDataValue(noData)
        try:
            for row in range(rows):
                self._getLines(row)
                self._calc(expression)
                tband.WriteArray(self.result, 0, row)
        except:
            print("Niepoprawne wyrazenie")
            pass
        tband.FlushCache()
        tband.ComputeStatistics(True)
        del tband
        target = None

