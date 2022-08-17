from requests_oauthlib import OAuth2Session
import requests
import hashlib
import base64
import logging
import json
import argparse

try:
    import webview  # Optional pywebview 3.0 or higher
except ImportError:
    webview = None
try:
    from selenium import webdriver  # Optional selenium 3.13.0 or higher
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
    webdriver = None

authorization_endpoint = 'https://api.enphaseenergy.com/oauth/authorize'
redirect_uri = 'https://api.enphaseenergy.com/oauth/redirect_uri'
token_uri = 'https://api.enphaseenergy.com/oauth/token'
cache_file = 'enphase.json'

parser = argparse.ArgumentParser(description='Sync car to solar.')
parser.add_argument('--clientid', help='enphase client id')
parser.add_argument('--clientsecret', help='enphase client secret')
parser.add_argument('--key', help='enphase key')
parser.add_argument('--systemid', help='enphase system id')
args = parser.parse_args()

def custom_auth(url):
    # Use pywebview if no web browser specified
    if webview:
        result = ['']
        window = webview.create_window('Login', url)
        def on_loaded():
            result[0] = window.get_current_url()
            if 'void/callback' in result[0].split('?')[0]:
                window.destroy()
        try:
            window.events.loaded += on_loaded
        except AttributeError:
            window.loaded += on_loaded
        webview.start()
        return result[0]
    # Use selenium to control specified web browser
    options = [webdriver.chrome,
               webdriver.edge][0].options.Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    with [webdriver.Chrome,
          webdriver.Edge][0](options=options) as browser:
        logging.info('Selenium opened %s', browser.capabilities['browserName'])
        browser.get(url)
        WebDriverWait(browser, 300).until(EC.url_contains('void/callback'))
        return browser.current_url

#default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#logging.basicConfig(level=logging.DEBUG, format=default_format)
def load_cache():
	try:
		with open(cache_file) as infile:
			cache = json.load(infile)
	except (IOError, ValueError):
		cache = {}
	return cache

def dump_cache(cache):
	""" Default cache dumper method """
	try:
		with open(cache_file, 'w') as outfile:
			json.dump(cache, outfile)
	except IOError:
		print('Cache not updated')
	else:
		print('Updated cache')

def token_updater(token):
    dump_cache(token)

def perform_auth(client):
	uri, state = client.authorization_url(authorization_endpoint)
	print(uri)
	response = custom_auth(uri)
	print(response)

	client.fetch_token(token_uri, authorization_response=response, client_secret=args.clientsecret)
	print(client.token)
	cache = client.token
	dump_cache(cache)

api_base = f'https://api.enphaseenergy.com/api/v4/systems/{args.systemid}'

def call_api(client, url):
  return json.loads(client.request('GET', url).text)

cache = load_cache()
client = OAuth2Session(client_id=args.clientid, redirect_uri=redirect_uri, auto_refresh_url=token_uri, token=cache, token_updater=token_updater)
if not client.authorized:
	perform_auth(client)
summary_api = api_base + f'/summary?key={args.key}'
res = call_api(client, summary_api)
print(res['current_power'])
