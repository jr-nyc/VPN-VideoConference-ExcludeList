# VPN-Exclude

A script and example Ansible play to generate a Cisco standard ASA ACL of Zoom, Webex, and Mircosoft Teams IPv4 addresses, so you can exclude Video traffic from your VPN tunnel.

If you don't run ASAs the `get'service_name'IPs` functions in the script collects the IPs from each services website, and puts them in a list for you.

## How to Use

### To collect the IPs: 
* `python3 generateASAVPNTunnelACL.py`
* The List of Subnets will be in roles/ASAVPNTunnelACL/var/main.yml

### To Deploy to your ASAs:
* ansible-playbook role-ASAVPNTunnelACL.yml -i 'your inventory'

### Where Webex, Zoom and MS Teams publish their Lists:
1. Webex:
* https://help.webex.com/en-us/WBX264/How-Do-I-Allow-Webex-Meetings-Traffic-on-My-Network#id_135011

2. Zoom:
* https://support.zoom.us/hc/en-us/articles/201362683-Network-Firewall-or-Proxy-Server-Settings-for-Zoom

3. MS Teams:
* https://docs.microsoft.com/en-us/microsoftteams/prepare-network

### Cisco ASA VPN Exlcude Documentation
https://www.cisco.com/c/en/us/td/docs/security/vpn_client/anyconnect/anyconnect46/administration/guide/b_AnyConnect_Administrator_Guide_4-6/configure-vpn.html#task_v4x_ydm_pbb