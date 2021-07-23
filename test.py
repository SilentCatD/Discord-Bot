import requests
api_key = 'd9dd7595f02577a2bf2b9f385ebc1c64'
base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name = 'Ho Chi Minh'
complete_url = base_url + "appid=" + api_key + "&q=" + city_name
response = requests.get(complete_url)
print(response.json())
