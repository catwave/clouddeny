#!/usr/bin/python3

# Based off : https://github.com/nccgroup/cloud_ip_ranges

'''Order Allow,Deny
Allow from all
Deny from '''

from argparse import ArgumentParser
import requests
from netaddr import IPNetwork, IPAddress
from lxml import html
import csv
import coloredlogs
import logging

def gather(args):

    all_ips = ''

    if args.block_aws:
        logger.info('Checking for AWS')
        aws_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        aws_ips = requests.get(aws_url, allow_redirects=True).json()
        
        for item in aws_ips["prefixes"]:
            all_ips += item["ip_prefix"] + " "

    if args.block_azure:
        azure_url = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
        page = requests.get(azure_url)
        tree = html.fromstring(page.content)
        download_url = tree.xpath("//a[contains(@class, 'failoverLink') and "
                                  "contains(@href,'download.microsoft.com/download/')]/@href")[0]

        azure_ips = requests.get(download_url, allow_redirects=True).json()
        for item in azure_ips["values"]:
            for prefix in item["properties"]['addressPrefixes']:
                all_ips += prefix + " "

    if args.block_gcp:
        logger.info('Checking for GCP')
        gcp_url = 'https://www.gstatic.com/ipranges/cloud.json'
        gcp_ips = requests.get(gcp_url, allow_redirects=True).json()

        for item in gcp_ips["prefixes"]:
            all_ips += str(item.get("ipv4Prefix")) + " "
        #TODO
        #for item in gcp_ips["prefixes"]:
            #all_ips += str(item.get("ipv6Prefix")) + " "

    if args.block_oci:
        logger.info('Checking for OCI')
        oci_url = 'https://docs.cloud.oracle.com/en-us/iaas/tools/public_ip_ranges.json'
        oci_ips = requests.get(oci_url, allow_redirects=True).json()

        for region in oci_ips["regions"]:
            for cidr_item in region['cidrs']:
                all_ips += cidr_item["cidr"] + " "

    if args.block_do:
        # This is the file linked from the digitalocean platform documentation website:
        # https://www.digitalocean.com/docs/platform/
        do_url = 'http://digitalocean.com/geo/google.csv'
        do_ips_request = requests.get(do_url, allow_redirects=True)

        do_ips = csv.DictReader(do_ips_request.content.decode('utf-8').splitlines(), fieldnames=[
            'range', 'country', 'region', 'city', 'postcode'
        ])

        for item in do_ips:
            all_ips += item['range'] + " "

    return all_ips


logger = logging.getLogger(__name__)
coloredlogs.install(level='info')

def main():
    parser = ArgumentParser(add_help=True, allow_abbrev=False)

    parser.add_argument('--aws', dest='block_aws', action='store_true',
                        help="Block aws IP range")
    parser.add_argument('--az', dest='block_azure', action='store_true',
                        help="Block azure IP range")
    parser.add_argument('--gcp', dest='block_gcp', action='store_true',
                        help="Block Google Cloud Provider IP range")
    parser.add_argument('--oci', dest='block_oci', action='store_true',
                        help="Block Oracle Cloud Infrastructure IP range")
    parser.add_argument('--do', dest='block_do', action='store_true',
                        help="Block Digital Ocean IP range")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help="Suppress logging output")

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel('CRITICAL')
    
    list = gather(args)

    print(__doc__ + list)

    logger.info('Done')

if __name__ == "__main__":
    main()