#!/usr/bin/env python

from pyVim import connect
import atexit
import getpass
from pyVmomi import vim
import sys
import webbrowser
import time
import requests
requests.packages.urllib3.disable_warnings()

i_host = raw_input(prompt='Enter VCenter IP: ')
i_user = raw_input(prompt='Enter login user: ')
i_pwd = getpass.getpass(prompt='Enter pwd: ')
vm_name = raw_input(prompt='Enter VM name: ')
vm_sso = raw_input(prompt='Enter VMWare SSO Server IP: ')
html_port = 7343
port = 443
si = None
conn_inst = None
vcenter_ip = None

def _get_vcenterSSLThumbprint(vcenter_ip):
    openssl_cmd = 'openssl s_client -connect '+i_host+':443< /dev/null 2>/dev/null | openssl x509 -fingerprint -noout -in /dev/stdin'
    import subprocess
    vcenterSSLThumbprint = subprocess.check_output(openssl_cmd, shell=True)
    return vcenterSSLThumbprint

def vmconnection(my_host,my_user,my_pwd):
    
    try:
        si = connect.SmartConnect(host=my_host,user=my_user,pwd=my_pwd)
    except vim.fault.InvalidLogin as e:
        print e.msg
        sys.exit()
    return si

def get_session_tkt(conn_inst):
    sm = conn_inst.content.sessionManager
    session_tkt = sm.AcquireCloneTicket()
    return session_tkt

def _get_MOR(service_instance,vm_name):
    si = service_instance
    name = vm_name
    content = si.RetrieveContent()
    vimtype = [vim.VirtualMachine]
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            esxi_host = str(obj.runtime.host.name)
            MOR_id = str(c)[5:-1]
    return MOR_id


conn_inst = vmconnection(i_host,i_user,i_pwd)
atexit.register(connect.Disconnect, si)

url = 'https://'+vm_sso+':7343/console/?vmId='+str(_get_MOR(conn_inst,vm_name))[15:-1]+'&vmName='+vm_name+'&host='+i_host+'&sessionTicket='+str(get_session_tkt(conn_inst))+'&thumbprint='+str(_get_vcenterSSLThumbprint(i_host))[17:].rstrip()

webbrowser.open_new(url)
time.sleep(60)