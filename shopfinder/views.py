from urllib2 import URLError

from django.contrib.gis import geos
from django.contrib.gis import measure
from django.shortcuts import render
from django.template import RequestContext
from geopy.geocoders import Bing
from geopy.geocoders.bing import GeocoderServiceError
from datetime import datetime

from shopfinder import forms
from shopfinder.models import Shop
from shopfinder.models import SearchData
from shopfinder.models import ShopSearch


def geocode_address(address):
    address = address.encode('utf-8')
    geocoder = Bing(api_key='AmTOjxQXZeKHxacoFI3IoPyR6PHW0U-r0NgDSQ8F-x0dt97mnLMFKREiS96mkOkX')
    try:
        location = geocoder.geocode(address)
    except (URLError, GeocoderServiceError, ValueError):
        pass
    else:
        return location

def get_shops(longitude, latitude):
    current_point = geos.fromstr("POINT(%s %s)" % (longitude, latitude))
    distance_from_point = {'km': 10}
    shops = Shop.gis.filter(location__distance_lte=(current_point, measure.D(**distance_from_point)))
    shops = shops.distance(current_point).order_by('distance')
    return shops.distance(current_point)

def save_search(rawAddr, locationDetails, shops):
    point = "POINT(%s %s)" % (locationDetails.longitude, locationDetails.latitude)
    loc = geos.fromstr(point)
    state = locationDetails.raw['address']['adminDistrict'] #Error Handling
    zipcode = locationDetails.raw['address']['postalCode']
    typedData = SearchData(typedData=rawAddr, state=state, zipcode=zipcode, location=loc)
    typedData.save()
    dt = str(datetime.utcnow())
    for shop in shops:
        shopData = ShopSearch(shop=shop, hit=typedData, dt=dt)
        shopData.save()

def home(request):
    form = forms.AddressForm()
    shops = []
    latitude = "0"
    longitude = "0"
    if request.POST:
        form = forms.AddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            location = geocode_address(address)
            if location:
                shops = get_shops(location.longitude, location.latitude)
                saveData = save_search(address, location, shops)
                latitude = location.latitude
                longitude = location.longitude

    return render(request,
        'home.html',
        {'form': form, 'latitude': latitude, 'longitude': longitude ,'shops': shops})