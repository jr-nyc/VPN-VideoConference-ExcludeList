# python3
# Generates Standard ACL to use in Cisco ASA's VPN ACLs for including or excluding from a tunnel
# Collects Webex, Zoom, Microsoft Teams, and static entrys and combines them into the acl
# Places file as main.yml under roles/ASAVPNTunnelACL/var/

import numpy as np
import pandas as pd
import ipaddress as ip
import yaml
import json
import uuid
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup

# pass IpList and description and returns standard ACL
def writeASAACL(ipList, remark):
    updateList = []
    # description for passed list
    updateList.append(f"access-list ASAVPNTunnelACL remark {remark}")

    # Loops through Ip list where they are in the format IP/notation
    for x in ipList:
        print(x)
        ipAddr, ipMask = splitIPMask(x)
        if ipAddr != "error":
            # print(type(ipMask))
            # ASA converts /32 to host Keyword
            if str(ipMask) == "255.255.255.255":

                updateList.append(
                    f"access-list ASAVPNTunnelACL standard permit host {ipAddr}"
                )
            else:
                updateList.append(
                    f"access-list ASAVPNTunnelACL standard permit {ipAddr} {ipMask}"
                )

    return updateList


# creates file to be placed in var folder for the role to call
def genACLFile(filename, *ipLists):
    ymlData = {}
    updateList = []
    # combines IP ACLs
    for x in ipLists:
        updateList.extend(x)

    ymlData["acl"] = updateList

    # print(yaml.dump(ymlData, default_flow_style=False))
    # outputs to file
    with open(filename, "w+") as outfile:
        yaml.dump(ymlData, outfile, default_flow_style=False, explicit_start=True)
    print(filename)


# Parses webage
def getHTMLContent(link):
    # adding try/except incase website does not allow scripting
    # https://stackoverflow.com/questions/3336549/pythons-urllib2-why-do-i-get-error-403-when-i-urlopen-a-wikipedia-page
    try:
        html = urlopen(link)
    except:
        req = urllib.request.Request(link, headers={"User-Agent": "Magic Browser"})
        html = urllib.request.urlopen(req)
        # print(html.read())
    soup = BeautifulSoup(html, "html.parser")

    return soup


# converts ip/notation to ip, netmask
def splitIPMask(ipAddrMask):
    try:
        ipAddr = ip.IPv4Interface(ipAddrMask)
        return (ipAddr.ip, ipAddr.netmask)
    except:
        print("error" + ipAddrMask)
        return ("error", ipAddrMask)


# static entries for ACL
def genStaticACL():
    # define Entries for your use
    staticList = ["access-list ASAVPNTunnelACL standard permit host 0.0.0.0"]
    return staticList


# Get  and parse the IPs for MS teams
def getMSTeamsIPs():

    # generate uuid and pull the json list of endpoint IDs from Microsoft
    # outputs in a list to uses with writeASAACL

    # https://docs.microsoft.com/en-us/microsoftteams/prepare-network
    # https://docs.microsoft.com/en-us/office365/enterprise/urls-and-ip-address-ranges#skype-for-business-online-and-microsoft-teams
    html = urlopen(
        "https://endpoints.office.com/endpoints/worldwide?clientrequestid={}".format(
            uuid.uuid4()
        )
    )
    res = json.loads(html.read())

    # Define the IDs of the stuff we care about. This will tell us which sections to parse of the returned json blob
    teams_ids = [11]
    for section in res:
        # Select Teams section
        if section["id"] in teams_ids:
            teamsIP = section["ips"]
    teamsACL = writeASAACL(teamsIP, "MS TEAMS Public IPs")
    return teamsACL


def getZoomIPs():
    # collects ZoomIPs
    # IPs under 'p' tag
    content = getHTMLContent(
        "https://support.zoom.us/hc/en-us/articles/201362683-Network-Firewall-or-Proxy-Server-Settings-for-Zoom"
    )

    zoomIP = []
    for p in content.find_all("p"):
        p_text = p.get_text(",")
        p_list = p_text.split(",")
        # finds first table with IP ranges
        if (len(p_list)) > 10:
            for x in p_list:
                if len(x) > 10:
                    zoomIP.append(x.strip())
            break

    zoomACL = writeASAACL(zoomIP, "zoom Public IPs")
    return zoomACL


def getWebexIPs():
    # collects webebx IPs
    # IPs under 'ul' tag
    content = getHTMLContent(
        "https://help.webex.com/en-us/WBX264/How-Do-I-Allow-Webex-Meetings-Traffic-on-My-Network"
    )

    webexIP = []
    for ul in content.find_all("ul"):
        ul_text = ul.get_text(",")
        if "CIDR" in ul_text:
            for x in ul_text.split():
                if "/" in x:
                    for y in x.split(","):
                        if "range" not in y:
                            webexIP.append(y)

    webexACL = writeASAACL(webexIP, "webex Public IPs")
    return webexACL


if __name__ == "__main__":
    zoomACL = getZoomIPs()
    MSTeamsACL = getMSTeamsIPs()
    webexACL = getWebexIPs()
    zoomACL = getZoomIPs()
    staticACL = genStaticACL()
    genACLFile(
        "roles/ASAVPNTunnelACL/var/main.yml", staticACL, zoomACL, webexACL, MSTeamsACL
    )
