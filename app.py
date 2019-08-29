from flask import Flask, request, jsonify, session, url_for, redirect, render_template
import os
import config
import requests
from urllib.parse import urlencode, quote_plus
from datetime import datetime

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
    temperature = int(weather['main']['temp'])
    description = weather['weather'][0]['description']
    main = weather['weather'][0]['main']
    icon = weather['weather'][0]['icon']
    ip = get_ip()
    city = ip['city']
    country = ip['country']
    lists = getweather3hr(lat, lon)
    if weather['cod'] == 200:
        return render_template('index.html', temperature=temperature, description=description, icon=icon, city=city, country=country,main=main, lists=lists)
    else:
        return redirect(url_for('error_404'))

def get_ip():
    #Get Ip address from user header
    if 'X-Forwarded-For' in request.headers:
        ip = str(request.headers['X-Forwarded-For'])
    else:
        ip = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    #get geolocation from IP Address
    r = requests.get('http://ip-api.com/json/{}'.format(ip))
    ip_api = r.json()
    if ip_api['status'] == 'success':
        return {
            'status': ip_api['status'],
            'city': ip_api['city'],
            "zip": ip_api['zip'],
            "lat": ip_api['lat'],
            "lon": ip_api['lon'],
            'country': ip_api['country'],
            'ip': ip_api['query']
        }
    else:
        print(ip_api)
        return None


def getweather3hr(lat,lon):
    params = {'lat': lat, 'lon': lon,
              'appid': config.WEATHER_KEY, 'units': 'metric'}
    result = urlencode(params, quote_via=quote_plus)
    weather_url = 'https://api.openweathermap.org/data/2.5/forecast?{}'.format(
        result)
    r = requests.get(weather_url)
    weather = r.json()
    listemp = []
    listdesc = []
    listmain = []
    listicon = []
    listime = []
    for i in range(1,7):
        listemp.append(int(weather['list'][i]['main']['temp']))
        listdesc.append(weather['list'][i]['weather'][0]['description'])
        listmain.append(weather['list'][i]['weather'][0]['main'])
        listicon.append(weather['list'][i]['weather'][0]['icon'])
        time = weather['list'][i]['dt_txt']
        xtime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        formtime = xtime.strftime("%H:%M:%S")
        listime.append(formtime)
    print(time)
    return {
        'temperature':listemp,
        'description':listdesc,
        'icon':listicon,
        'time':listime,
        'main':listmain
    }


def get_loc():
    ip = get_ip()
    city = ip.get('city')
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


@app.errorhandler(404)
def error_404(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)

'2019-08-29 12:00:00'
