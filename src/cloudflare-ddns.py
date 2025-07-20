#!/usr/bin/env python3
#------------------------------------------------------------------------------
#  Copyright (c) 2024-2025 LucAce
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
#------------------------------------------------------------------------------
#  Cloudflare Dynamic DNS Docker Application
#  File: cloudflare-ddns.py
#
#  Functional Description:
#
#      A script that updates a Cloudflare DNS entry with the system's
#      public IPv4 address.
#
#  Docker Command:
#
#      CMD ["/usr/bin/python3", "/app/cloudflare-ddns.py"]
#
#------------------------------------------------------------------------------

import sys
import ipaddress
import json
import logging
import os
import requests
import time
import traceback


#------------------------------------------------------------------------------
# Global Attributes
#------------------------------------------------------------------------------

# Default Domain Time to Live (in seconds)
DEFAULT_DOMAIN_TTL  = 3600

# Default Public IP Address Polling Rate (in seconds)
DEFAULT_UPDATE_RATE = 900


#------------------------------------------------------------------------------
# Logging Configuration
#------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)


#------------------------------------------------------------------------------
# CloudflareDDNS
# Class provides Cloudflare DDNS functions.
#------------------------------------------------------------------------------
class CloudflareDDNS():

    #--------------------------------------------------------------------------
    # Function: __init__
    # CloudflareDDNS object constructor.
    #
    # Parameters:
    # api_key     - Cloudflare API Key
    # zone_id     - Cloudflare DNS Zone ID
    # domain_name - Domain Name
    # domain_ttl  - Domain Time to Live
    #--------------------------------------------------------------------------
    def __init__(self, api_key, zone_id, domain_name, domain_ttl):
        self.api_key     = api_key
        self.zone_id     = zone_id
        self.domain_name = domain_name
        self.domain_ttl  = domain_ttl

        self.record_id   = None
        self.ipv4        = None
        self.ipv4_lkg    = None


    #--------------------------------------------------------------------------
    # Function: update
    # Update the DNS record.
    #--------------------------------------------------------------------------
    def update(self):

        # Get the Public IPv4 Address
        if not self.get_public_ipv4():
            logging.error("Unable To Get Public IPv4 Address")
            return

        logging.debug("Successfully Retrieved Public IPv4: " + str(self.ipv4))

        # Return if the IP address has not changed from the last update
        if self.ipv4 == self.ipv4_lkg:
            logging.info("DNS Record Current: " + str(self.domain_name) + ". " + \
                         str(self.domain_ttl) + " IN A " + str(self.ipv4))
            return

        # Get the Cloudflare Zone Record ID of the DNS entry
        if not self.get_cloudflare_dns_record_id():
            logging.error("Unable To Get Cloudflare DNS Record ID")
            return

        logging.debug("Successfully Retrieved Record ID: " + str(self.record_id))

        # Update the DNS entry
        if not self.update_cloudflare_dns_record():
            logging.error("Unable To Update Cloudflare DNS Record")
            return

        # Set last known good on successful update
        self.ipv4_lkg = self.ipv4

        logging.info("Updated DNS Record: " + str(self.domain_name) + ". " + \
                     str(self.domain_ttl) + " IN A " + str(self.ipv4))


    #--------------------------------------------------------------------------
    # Function: get_public_ipv4
    # Request the public IPv4 address from ipify.org.
    #
    # Returns:
    # bool - True if successful; False otherwise
    #--------------------------------------------------------------------------
    def get_public_ipv4(self):
        self.ipv4     = None
        response_data = None

        # Get the IPv4 address from Cloudflare's trace
        try:
            # Query for the public IPv4 address
            response = requests.get('https://api.cloudflare.com/cdn-cgi/trace')

            # Raise an exception if a non-valid status was returned
            response.raise_for_status()

            # Find and extract the ip value
            for line in response.iter_lines():
                line_utf8 = line.decode('utf-8')

                if 'ip=' in line_utf8:
                    ipv4 = line_utf8.split('ip=')[1].split()[0]

            # Validate the response data
            self.ipv4 = format(ipaddress.IPv4Address(ipv4))

            # Return True if no exceptions were raised
            return True

        except:
            # Return False on any exception
            logging.debug("Public IPv4 Request from Cloudflare Failed")
            pass

        # Fall back to ipify for IPv4 if first attempt failed
        try:
            # Query for the public IPv4 address
            response = requests.get('https://api.ipify.org?format=json')

            # Raise an exception if a non-valid status was returned
            response.raise_for_status()

            # Store the response as JSON formatted data
            response_data = response.json()

            # Validate and parse the response data
            self.ipv4 = format(ipaddress.IPv4Address(response_data.get("ip")))

            # Return True if no exceptions were raised
            return True

        except:
            # Return False on any exception
            logging.debug("Public IPv4 Request from ipify Failed")
            return False


    #--------------------------------------------------------------------------
    # Function: get_cloudflare_dns_record_id
    # Query Cloudflare for the Record ID associated with the A entry.
    #
    # Returns:
    # bool - True if successful; False otherwise
    #--------------------------------------------------------------------------
    def get_cloudflare_dns_record_id(self):
        self.record_id = None

        # Zone ID Records API URL
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records'

        # API Header
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            # Query for the Record IDs
            response = requests.get(url, headers=headers)

            # Raise an exception if a non-valid status was returned
            response.raise_for_status()

            # Store the response as JSON formatted data
            response_data = response.json()

        except:
            # Return False on any exception
            logging.debug("Record ID Request Failed")
            return False

        # Verify the query was successful
        if ( not ("success" in response_data and
                  "result"  in response_data and
                  str(response_data["success"]).lower() == "true" and
                  len(response_data["result"]) > 0) ):
            logging.debug("Record ID Query Unsuccessful")
            return False

        # Search for the Record ID of the entry
        for entry in response_data["result"]:
            if ( "id"   in entry and
                 "type" in entry and
                 "name" in entry and
                 str(entry["type"].upper()) == "A" and
                 str(entry["name"].lower()) == str(self.domain_name).lower() ):
                self.record_id = str(entry["id"]).lower()
                return True

        # Return False if the Record ID was not found
        logging.debug("Record ID Not Found")
        return False


    #--------------------------------------------------------------------------
    # Function: update_cloudflare_dns_record
    # Update the Cloudflare A type DNS entry record.
    #
    # Returns:
    # bool - True if successful; False otherwise
    #--------------------------------------------------------------------------
    def update_cloudflare_dns_record(self):
        # Zone Record ID API URL
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{self.record_id}'

        # API Header
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Data Fields
        data = {
            'type': 'A',
            'name': f'{self.domain_name}',
            'content': f'{self.ipv4}',
            'ttl': int(self.domain_ttl)
        }

        try:
            # Update the DNS record
            response = requests.put(url, json=data, headers=headers)

            # Raise an exception if a non-valid status was returned
            response.raise_for_status()

            # Store the response as JSON formatted data
            response_data = response.json()

        except:
            # Return False on any exception
            logging.debug("DNS Record Request Failed")
            return False

        # Verify the query was successful
        if ( not ("success" in response_data and
                  "result"  in response_data and
                  str(response_data["success"]).lower() == "true") ):
            logging.debug("DNS Record Query Unsuccessful")
            return False

        # Verify the request's contents
        if ( "id"      in response_data["result"] and
             "name"    in response_data["result"] and
             "type"    in response_data["result"] and
             "content" in response_data["result"] and
             str(response_data["result"]["id"]).lower()   == str(self.record_id).lower()   and
             str(response_data["result"]["name"]).lower() == str(self.domain_name).lower() and
             str(response_data["result"]["type"]).upper() == "A"                           and
             str(response_data["result"]["content"])      == str(self.ipv4).lower() ):
            return True
        else:
            logging.debug("DNS Record Not Found")
            return False


#------------------------------------------------------------------------------
# Function: main
# Main execution function.
#------------------------------------------------------------------------------
def main():

    # Get optional VERBOSE environment variable
    verbose = os.environ.get('VERBOSE')
    if ((verbose is not None) and (verbose.lower() == "true")):
        logging.getLogger().setLevel(logging.DEBUG)

    # Get required CLOUDFLARE_API_KEY environment variable
    cloudflare_api_key = os.environ.get('CLOUDFLARE_API_KEY')
    if cloudflare_api_key is None:
        logging.error("Missing Required Environment Variable: CLOUDFLARE_API_KEY")
        sys.exit(1)
    else:
        logging.debug("Using provided CLOUDFLARE_API_KEY value")

    # Get required CLOUDFLARE_ZONE_ID environment variable
    cloudflare_zone_id = os.environ.get('CLOUDFLARE_ZONE_ID')
    if cloudflare_zone_id is None:
        logging.error("Missing Required Environment Variable: CLOUDFLARE_ZONE_ID")
        sys.exit(1)
    else:
        logging.debug("Using provided CLOUDFLARE_ZONE_ID value")

    # Get required DOMAIN_NAME environment variable
    domain_name = os.environ.get('DOMAIN_NAME')
    if domain_name is None:
        logging.error("Missing Required Environment Variable: DOMAIN_NAME")
        sys.exit(1)
    else:
        logging.debug("Using provided DOMAIN_NAME value")

    # Get optional DOMAIN_TTL environment variable
    domain_ttl = int(os.environ.get('DOMAIN_TTL'))
    if isinstance(domain_ttl, int):
        logging.debug("Using provided DOMAIN_TTL value")
    else:
        logging.debug("Using default DOMAIN_TTL value")
        domain_ttl = int(DEFAULT_DOMAIN_TTL)

    # Get optional UPDATE_RATE environment variable
    update_rate = int(os.environ.get('UPDATE_RATE'))
    if isinstance(update_rate, int):
        logging.debug("Using provided UPDATE_RATE value")
    else:
        logging.debug("Using default UPDATE_RATE value")
        update_rate = int(DEFAULT_UPDATE_RATE)

    # Create update object
    ddns = CloudflareDDNS(
        cloudflare_api_key, cloudflare_zone_id, domain_name, domain_ttl
    )

    # Loop forever
    while True:
        ddns.update()
        time.sleep(update_rate)

    sys.exit(1)


#------------------------------------------------------------------------------
# Call main()
#------------------------------------------------------------------------------
if __name__ == "__main__":

    try:
        main()

    except Exception as e:
        traceback.print_exc()
        logging.error(f"Unexpected exception: {e}")
        sys.exit(1)
