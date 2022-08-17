import subprocess
import time
import json
import schedule
import requests
from os.path import exists
import logging
import argparse
import os

config_file = 'config'

def load_config():
	with open(config_file) as infile:
		config = json.load(infile)
		return config

config = load_config()

def get_current_power():
	cmd = ['python3', 'enphase.py', '--clientid', config["client_id"], '--clientsecret', config["client_secret"], '--key', config["key"], '--systemid', config["system_id"]]
	ret = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
	return int(ret.stdout.splitlines()[-1])

def get_tesla_list():
	cmd = ['python3', 'tesla.py', '-e', config["tesla_email"], '-l']
	subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

def set_tesla_charging(amps):
	cmd = ['python3', 'tesla.py', '-e', config["tesla_email"], '-a', 'CHARGING_AMPS', '-k', f'charging_amps={amps}', '-w']
	subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

def fetch_charger():
	ip = config["tesla_charger_ip"]
	url = f'http://{ip}/api/1/vitals'
	return json.loads(requests.get(url).text)['vehicle_connected']

def refresh_tokens():
	logging.info('refreshing tokens')
	get_tesla_list()
	get_current_power()

def is_solar_sync_on():
        cwd = os.getcwd()
        return exists(f'{cwd}/on')

def run_steps():
        charger = fetch_charger()
        solar_sync = is_solar_sync_on()
        logging.info(f'charger connected={charger} sync={solar_sync}')
        if charger and solar_sync:
                power = get_current_power()
                amps = int(max(power / 240, config["min_power"] / 240))
                amps = min(amps, config["max_amps"])
                logging.info(f'setting amps={amps} power={power}')
                set_tesla_charging(amps)	
		
parser = argparse.ArgumentParser(description='Sync car to solar.')
parser.add_argument('-i', '--init', action='store_true', help='initialize')
args = parser.parse_args()

logging.basicConfig(filename='logs/solarsync', encoding='utf-8', level=logging.INFO)

refresh_tokens()
run_steps()

if not args.init:
	schedule.every(10).minutes.do(run_steps);
	schedule.every().day.do(refresh_tokens)

	while True:
		schedule.run_pending()
		time.sleep(1)
