#!/usr/bin/python

import httplib
import socket
import re

host = 'www.cnn.com'
def is_website_online(host):
    """ This function checks to see if a host name has a DNS entry by checking
        for socket info. If the website gets something in return, 
        we know it's available to DNS.
    """
    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        return False
    else:
        return True


def is_page_available(host, path="/"):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        False.
    """
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        if re.match("^[23]\d\d$", str(conn.getresponse().status)):
            return True
    except StandardError:
        return None

