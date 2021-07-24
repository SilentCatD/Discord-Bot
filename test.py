import requests
url = 'https://zenquotes.io/api/random'
response = requests.get(url)
response = response.json()
print(response[0]['q'] + " - " + response[0]['a'])
