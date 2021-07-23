import requests
API_key = 'd715f170763664cefb4ba83e161e58f9'
city_name = 'Ho Chi Minh'
response = requests.get('https://api.covid19api.com/summary')
print(response.json())