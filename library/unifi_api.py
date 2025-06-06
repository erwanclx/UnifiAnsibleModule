#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r'''
---
module: unifi_api
short_description: Make API requests to the Ubiquiti UniFi API
description:
    - Make API requests to the Ubiquiti UniFi API

version_added: "0.1.1"

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

- name: Get a specific host
  unifi_api:
    endpoint: "hosts/1234567890abcdef"
    method: GET
    headers: "{{ headers }}"
    api_key: "{{ unifi_api_key }}"
  register: host

- name: Check firmware update availability for a specific host
  when: host.result is defined
  debug:
    msg: "Host {{ host.hostname }} has firmware update available: {{ host.firmware_update_available }} (version: {{ host.firmware_update_version }})"
'''

class UbiquitiAPIClient:
    def __init__(self, api_key, headers, base_url="https://api.ui.com/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.headers["X-API-KEY"] = api_key

    def request(self, method, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.request(method, url, json=params or {})
        response.raise_for_status()
        return response.json().get("data", {})

class HostParser:
    @staticmethod
    def parse(data):
        def extract_info(host):
            reported = host.get("reportedState", {})
            device_state = reported.get("deviceState", "")
            hostname = reported.get("hostname", "")
            hardware = reported.get("hardware", {}) if isinstance(reported.get("hardware", {}), dict) else {}
            firmware = reported.get("firmwareUpdate", {}) if isinstance(reported.get("firmwareUpdate", {}), dict) else {}

            return {
                "hostname": hostname,
                "firmware_update_available": device_state == "updateAvailable",
                "firmware_update_version": firmware.get("latestAvailableVersion", ""),
                "current_version": hardware.get("firmwareVersion", "")
            }

        if isinstance(data, list):
            return [extract_info(h) for h in data]
        return extract_info(data)

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

    try:
        endpoint = module.params["endpoint"]
        client = UbiquitiAPIClient(
            api_key=module.params["api_key"],
            headers=module.params["headers"]
        )
        data = client.request(
            method=module.params["method"],
            endpoint=endpoint,
            params=module.params["params"]
        )

        result = HostParser.parse(data) if endpoint.startswith("hosts") else {}

        module.exit_json(changed=False, result=result)

    except requests.exceptions.HTTPError as e:
        module.fail_json(msg=f"HTTP error: {e}", status_code=e.response.status_code, response=e.response.text)
    except requests.exceptions.RequestException as e:
        module.fail_json(msg=f"Request error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()