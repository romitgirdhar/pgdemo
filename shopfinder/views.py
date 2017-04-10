from urllib2 import URLError

from django.contrib.gis import geos
from django.contrib.gis import measure
from django.shortcuts import render
from django.template import RequestContext
from geopy.geocoders import Bing
from geopy.geocoders.bing import GeocoderServiceError

from shopfinder import forms
from shopfinder import models


def geocode_address(address):
    address = address.encode('utf-8')
    geocoder = Bing(api_key='AmTOjxQXZeKHxacoFI3IoPyR6PHW0U-r0NgDSQ8F-x0dt97mnLMFKREiS96mkOkX')
    try:
        _, latlon = geocoder.geocode(address)
    except (URLError, GeocoderServiceError, ValueError):
        return None
    else:
        return latlon

def get_shops(longitude, latitude):
    current_point = geos.fromstr("POINT(%s %s)" % (longitude, latitude))
    distance_from_point = {'km': 10}
    shops = models.Shop.gis.filter(location__distance_lte=(current_point, measure.D(**distance_from_point)))
    shops = shops.distance(current_point).order_by('distance')
    return shops.distance(current_point)

def home(request):
    form = forms.AddressForm()
    shops = []
    latitude = 0
    longitude = 0
    if request.POST:
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            location = geocode_address(address)
            if location:
                latitude, longitude = location
                shops = get_shops(longitude, latitude)

    return render(request,
        'home.html',
        {'form': form, 'latitude': latitude, 'longitude': longitude ,'shops': shops})