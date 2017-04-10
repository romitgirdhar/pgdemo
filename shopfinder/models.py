from django.contrib.gis.db import models as gis_models
from django.contrib.gis import geos
from django.db import models
from geopy.geocoders import Bing
from geopy.geocoders.bing import GeocoderServiceError
from urllib2 import URLError


class Shop(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    location = gis_models.PointField(u"longitude/latitude",
                                     geography=True, blank=True, null=True)

    gis = gis_models.GeoManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if not self.location:
            address = u'%s %s' % (self.city, self.address)
            address = address.encode('utf-8')
            geocoder = Bing(api_key='AmTOjxQXZeKHxacoFI3IoPyR6PHW0U-r0NgDSQ8F-x0dt97mnLMFKREiS96mkOkX')
            try:
                _, latlon = geocoder.geocode(address)
            except (URLError, GeocoderServiceError, ValueError):
                pass
            else:
                point = "POINT(%s %s)" % (latlon[1], latlon[0])
                self.location = geos.fromstr(point)
        super(Shop, self).save()

class SearchData(models.Model):
    typedData = models.CharField(max_length=500)
   # city = models.CharField(max_length=50) for later
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=5)
    location = gis_models.PointField(u"longitude/latitude",
                                     geography=True, blank=True, null=True)

 #   def save(self, **kwargs):
 #       if not self.location:
 #           address = self.typedData
 #           address = address.encode('utf-8')
 #           geocoder = Bing(api_key='AmTOjxQXZeKHxacoFI3IoPyR6PHW0U-r0NgDSQ8F-x0dt97mnLMFKREiS96mkOkX')
 #           try:
 #               location = geocoder.geocode(address)
 #           except (URLError, GeocoderServiceError, ValueError):
 #               pass
 #           else:
 #               addrArr = location.raw['displayName'].split(',')
 #               self.state = addrArr[len(addrArr)-3]
 #               self.zipcode = addrArr[len(addrArr)-2]
 #               point = "POINT(%s %s)" % (location.latitude, location.longitude)
 #               self.location = geos.fromstr(point)
 #       super(SearchData, self).save()
    
    def __unicode__(self):
        return self.typedData

class ShopSearch(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    hit = models.ForeignKey(SearchData, on_delete=models.CASCADE)
    dt = models.DateTimeField()

    def __unicode__(self):
        return self.dt
