import requests
import pprint


api_key = 'c18c40053572110cfdb4e76a96fe91f9'
lat =-29.9713841
long = -51.168997

pp = pprint.PrettyPrinter(indent=4)


response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&appid={api_key}")
clima = response.json()

pp.pprint(clima)