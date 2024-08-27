# UnifiAnsibleModule

A collection of Ansible modules for managing Ubiquiti Unifi devices, based on the new [Unifi API](https://developer.ui.com/unifi-api/) (Current : version 0.1).

## Requirements
- Python 3
- Ansible

## Installation
1. Clone the repository
2. Copy the `library` directory to your Ansible project
3. Create a `secrets.yml` file in the root of your project with the following content:
```yaml
unifi_api_key: "your_api_key"
```
4. Import the modules in your playbooks (you can test the modules by running the `test_playbook.yml` playbook)