import os
from osgeo import gdal
from os.path import basename, splitext

os.chdir(os.path.join(os.path.expanduser("~"), "Documents", "dist"))
lista = os.listdir(".")


class rast:
    def __init__(self, *lista):
        self.rasters = []
        self.metadata = []
        for r in lista:
            raster = gdal.Open(r)
            self.rasters.append(raster)
            print (raster == None)
            self.metadata.append(self.__getMetadata(raster))

        self.names = self.__getNames(*lista)
        # self.names = None
        self.__summary()

    def __getMetadata(self, raster):
        geoTransform = raster.GetGeoTransform()
        self.size = (raster.RasterXSize, raster.RasterYSize)
        self.projection = raster.GetProjection()
        self.resolution = (abs(geoTransform[1]), abs(geoTransform[5]))
        minX = geoTransform[0]
        maxY = geoTransform[3]
        maxX = minX + geoTransform[1] * self.size[0]
        minY = maxY + geoTransform[5] * self.size[1]
        self.extent = (minX, maxX, minY, maxY)
        return (self.size, self.projection, self.resolution, self.extent)

    def __getNames(self, *lista):
        return ([basename(splitext(raster)[0]) for raster in lista])

    def _getLines(self, row):
        self.__data = np.empty([len(self.rasters), self.size[0]])
        for ptr in self.rastry:
            p = ptr.GetRasterBands(1).readAsArray(0, row, self.size[0], 1)
            for i in range(len(rastry)):
                self.__data[i] = p

    def __calc(self, expression):
        dct = dict(zip(self.names, self.__data))
        self.result = np.zeros(size[0])
        self.result.shape = (1, size[0])
        self.result[0] = eval(expression, dct)

    def __summary(self):
        print("Name:{0:s}\n".format(self.names))

    def __calculator(self):
        pass