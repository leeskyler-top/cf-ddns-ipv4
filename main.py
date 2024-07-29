import json
import sys
from datetime import datetime

import requests
import re


def getip(api, keyname, regex):
    if keyname == "":
        data = requests.get(api, verify=False)
        ip = re.findall(regex, data.text)
        if len(ip) == 0:
            print("No IP found")
            sys.exit(1)
        else:
            return ip[0]
    else:
        data = requests.get(api, verify=False)
        if data.status_code == 200:
            data = data.json()
            return data[keyname]
        else:
            sys.exit(1)


def verify_token():
    global headers
    data = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify", verify=False, headers=headers)
    if data.status_code != 200:
        print("Invalid token", "HTTP Status Code:" + str(data.status_code))
        print(data.json())
        sys.exit(1)
    else:
        return data.json()['result']['id']


def get_zone_id(zone_name):
    global headers
    data = requests.get("https://api.cloudflare.com/client/v4/zones", verify=False, headers=headers,
                        params={'name': zone_name})
    data = data.json()
    filtered_result = [item for item in data['result'] if item['name'] == zone_name]
    if len(filtered_result) == 0 or filtered_result[0]['status'] != "active":
        print("Zone not found or not active")
        sys.exit(1)
    # Print the filtered result
    return filtered_result[0]['id']


def get_record_id(zone_id, ddns_domain, myip):
    global headers
    data = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=headers, verify=False)
    data = data.json()
    print(data)
    filtered_result = [item for item in data['result'] if item['name'] == ddns_domain and item['type'] == 'A']
    if len(filtered_result) == 0:
        create_record(zone_id, ddns_domain, myip)
    return filtered_result[0]['id'], filtered_result[0]['content']

def create_record(zone_id, ddns_domain, myip):
    global headers
    data = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", verify=False, headers=headers,
                         data=json.dumps({
                             "id": zone_id,
                             "content": myip,
                             "name": ddns_domain,
                             "proxied": False,
                             "type": "A",
                             "comment": "",
                             "TTL": 60,
                         }))
    print(data.status_code)
    sys.exit(0)

def update_record(zone_id, record_id, ddns_name, myip):
    global headers
    now = datetime.now()
    data = requests.patch(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}", verify=False, headers=headers, data=json.dumps({
        "id": zone_id,
        "name": ddns_name,
        "content": myip,
        "proxied": False,
        "type": "A",
        "comment": str(now.strftime("%Y-%m-%d %H:%M:%S")),
        "ttl": 60,
    }))
    print(data.status_code)
    sys.exit(0)


if __name__ == '__main__':
    # Open and read the config.json file
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Access the data using dictionary keys
    get_ip_api = config.get("get_ip_api")
    get_ip_api_key = config.get("get_ip_api_key")
    token = config.get("token")
    domain = config.get("domain")
    ddns_domain = config.get("ddns_domain")
    regex = config.get("get_ip_api_regex")

    myip = getip(get_ip_api, get_ip_api_key, regex)
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    account_id = verify_token()
    zone_id = get_zone_id(domain)
    record_id, content = get_record_id(zone_id, ddns_domain, myip)
    if content != myip:
        update_record(zone_id, record_id, ddns_domain, myip)
    else:
        print("The record is correct.")
        sys.exit(0)
