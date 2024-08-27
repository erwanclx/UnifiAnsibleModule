#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r'''
---
module: unifi_api
short_description: Make API requests to the Ubiquiti UniFi API
description:
    - Make API requests to the Ubiquiti UniFi API

version_added: "0.1.0"

options:
    api_key:
        description:
            - The API key to use for authentication
        required: true
        type: str
    endpoint:
        description:
            - The API endpoint to call
        required: true
        type: str
    params:
        description:
            - The parameters to include in the request
        required: false
        type: dict
        default: {}

author:
    - "Erwan Cloux (@erwanclx)"
'''

EXAMPLES = r'''
- name: Get all hosts
    unifi_api:
      endpoint: "hosts"
      method: GET
      headers: "{{ headers }}"
      api_key: "{{ unifi_api_key }}"
'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type='str'),
            method=dict(default="GET", choices=["GET", "POST", "PUT", "DELETE"]),
            headers=dict(required=True, type='dict'),
            api_key=dict(required=True, type='str', no_log=True),
            params=dict(required=False, type='dict', default={}),
        )
    )

    endpoint = module.params['endpoint']
    method = module.params['method']
    headers = module.params['headers']
    headers['X-API-KEY'] = module.params['api_key']
    params = module.params['params']

    url = f"https://api.ui.com/ea/{endpoint}"

    try:
        response = requests.request(method, url, headers=headers, json=params)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.HTTPError as http_err:
        module.fail_json(msg=f"HTTP error occurred: {http_err}")
    except Exception as err:
        module.fail_json(msg=f"Error occurred: {err}")
    
    module.exit_json(changed=False, result=result)

if __name__ == '__main__':
    main()
