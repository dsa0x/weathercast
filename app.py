from flask import Flask, request, jsonify, session, url_for, redirect
import os
import config
import requests
from urllib.parse import urlencode, quote_plus

app = Flask(__name__)
app.config['SECRET_KEY'] = "os.environ.get('SECRET')"


@app.route('/', methods=['GET', 'POST'])
def index():
    loc = get_loc()
    lat = loc['lat']
    lon = loc['lon']
    return redirect(url_for('weather',lat=lat,lon=lon))


@app.route('/<lat>/<lon>', methods=['GET', 'POST'])
def weather(lat, lon):
    params = {'lat': lat, 'lon': lon,
              'appid': config.WEATHER_KEY, 'units': 'metric'}
    result = urlencode(params, quote_via=quote_plus)
    weather_url = 'https://api.openweathermap.org/data/2.5/weather?{}'.format(
        result)
    r = requests.get(weather_url)
    weather = r.json()
    if weather['cod'] == 200:
        return {
            'Temperature': weather['main']['temp'],
            'Weather Description': weather['weather'][0]['description']
        }
    else:
        return None

def get_ip():
    #Get Ip address from user header
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    print('nawaoooo'+ip)
    #get geolocation from IP Address
    r = requests.get('http://ip-api.com/json/{}'.format(ip))
    ip_api = r.json()
    if ip_api['status'] != 'success':
        return None
    return {
        'status': ip_api['status'],
        'city': ip_api['city'],
        "zip": ip_api['zip'],
        "lat": ip_api['lat'],
        "lon": ip_api['lon'],
        'country': ip_api['country'],
        'ip': ip_api['query']
    }



def get_loc():
    ip = get_ip()
    city = ip['city']
    zipcode = ip['zip']
    url = 'http://www.datasciencetoolkit.org/maps/api/geocode/json?address={}+{}'.format(str(city),str(zipcode))
    r = requests.get(url)
    loc_details = r.json()
    if loc_details['status'] == 'OK':
        return {
            'lat': loc_details['results'][0]['geometry']['location']['lat'],
            'lon': loc_details['results'][0]['geometry']['location']['lng'],
        }
        
    else:
        return None




if __name__ == '__main__':
    app.run()
