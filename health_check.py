import sys
import yaml
import time
import requests
from pprint import pprint  
from urllib.parse import urlparse

# Returns the status of the enpoint API call
def check_endpoint(entry:dict):
    url = entry['url']
    headers = entry['headers'] if 'headers' in entry else None
    body = entry['body'] if 'body' in entry else None

    start = time.time() 
    if 'method' in entry and entry['method'] == 'POST':
        response = requests.post(url=url, headers=headers, json=body)
    else:
        response = requests.get(url=url, headers=headers, json=body)
    status_code = response.status_code
    end = time.time()
    time_taken = 1000 * (end - start)

    status = 'DOWN'
    if time_taken < 500 and status_code in range(200,299):
        status = 'UP'

    return status

# input is a list of dicts, each dict has a domain that needs to be accounted for
def check_file(input:list):
    domains = {}
    for entry in input:
        endpoint = entry['url']
        domain = urlparse(endpoint).netloc
        if domain not in domains:
            domains[domain] = [check_endpoint(entry)]
        else:
            domains[domain].append(check_endpoint(entry))
    
    percentages = {}
    for domain in domains:
        ups = 0
        requests = 0
        for item in domains[domain]:
            requests += 1
            if item == 'UP':
                ups += 1
        percentages[domain] = str(round((ups/requests)*100)) + '%'

    for domain in percentages:
        print(domain + ' has ' + percentages[domain] + ' availability percentage')     

def main():
    # If there is a command line argument and the file exists:
        # Run an infinite loop that can only be interrupted by CTRL+C
        # At 0 seconds and then every 15 seconds, do the HTTP request specified            

    if len(sys.argv) == 2:
        yaml_file = sys.argv[1]
        with open(yaml_file) as file:
            try:
                input = yaml.safe_load(file)
                try:
                    while True:
                        check_file(input)
                        time.sleep(15)
                except KeyboardInterrupt:
                    sys.exit(0)
            except yaml.YAMLError as exc:
                print(exc)
    else:
        print('Incorrect Formatting: Please specify a yaml file in the command line')

if __name__ == "__main__":
    main()