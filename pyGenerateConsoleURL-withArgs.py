#!/usr/bin/env python

from pyVim import connect
import atexit
import getpass
from pyVmomi import vim
import sys
import webbrowser
import time
import argparse
import requests
requests.packages.urllib3.disable_warnings()

def get_args():
    import argparse
    parser = argparse.ArgumentParser()

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere server to connect to')
    parser.add_argument('-d', '--domain',
                        required=True,
                        action='store',
                        help='login domain to use with username')
    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host. If blank, a secure input will be provided')
    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='Name of the virtual_machine to look for.')
    parser.add_argument('-o', '--ssosrv',
                        required=True,
                        action='store',
                        help='IP of SSO server')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(prompt='Enter pwd for host %s and user %s:' %  (args.host,args.user))
    return  args

def _create_char_spinner():
    """Creates a generator yielding a char based spinner.
        """
    while True:
        for c in '|/-\\':
            yield c

_spinner = _create_char_spinner()

def spinner(label=''):
    """Prints label with a spinner.
        When called repeatedly from inside a loop this prints
        a one line CLI spinner.
        """
    sys.stdout.write("\r\t%s %s" % (label, _spinner.next()))
    sys.stdout.flush()


def _get_MOR(service_instance,vm_name):
    si = service_instance
    name = vm_name
    content = si.RetrieveContent()
    vimtype = [vim.VirtualMachine]
    obj = None
    spinner()

    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            esxi_host = str(obj.runtime.host.name)
            MOR_id = str(c)[20:-1]
    return MOR_id


def _get_vcenterSSLThumbprint(i_host):
    import subprocess
    openssl_cmd = 'openssl s_client -connect '+i_host+':443< /dev/null 2>/dev/null | openssl x509 -fingerprint -noout -in /dev/stdin'
    spinner()
    vcenterSSLThumbprint = subprocess.check_output(openssl_cmd, shell=True)
    ssl_thumbprint = str(vcenterSSLThumbprint)[17:].rstrip()
    return ssl_thumbprint

def get_session_tkt(si):
    sm = si.content.sessionManager
    spinner()

    try:
        session_tkt = sm.AcquireCloneTicket()
    except:
        sys.exit()

    return session_tkt

## Test to make sure Vcenter server is available
def vcenter_alive(i_host):
    from subprocess import call, STDOUT
    ip = i_host
    ret = call("ping -c 1 %s" % ip,
               shell=True,
               stdout=open('/dev/null','w'),
               stderr=STDOUT)
    if ret == 0:
        #print "%s: is alive" % ip
        return True
    else:
        #print "%s: did not respond" % ip
        return False

## Setup the connection to the VCenter
def vmconnection(my_host,my_user,my_pwd):     
        try:
            si = connect.SmartConnect(host=my_host,user=my_user,pwd=my_pwd)
        except vim.fault.InvalidLogin as e:
            print e.msg
            #exit('Invalid login credential.  Check and try again!!')
        except vim.fault.InvalidLocale as e:
            print e.msg
            #exit('Incorrect locale, please try again')
        except vim.fault.NoPermission as e:
            print e.msg
            #exit('Incorrect permissions, contact your Virtual admin to get correct persmissions')
        else:
            return si

def main():
    retry = 0
    while retry < 5:
        args = get_args()
        i_host = args.host
        i_user = args.domain+'\\'+args.user
        i_pwd = args.password
        vm_name = args.name
        vm_sso = args.ssosrv
        retry +=1
        if vcenter_alive(i_host) == True:
            spinner()
            si = vmconnection(i_host,i_user,i_pwd)
            if si:
                print "Got the VM, building URL now, stand by..."
                atexit.register(connect.Disconnect, si)
                MOR_id = _get_MOR(si,vm_name)
                sess_tkt = get_session_tkt(si)
                ssl_tp = _get_vcenterSSLThumbprint(i_host)
                url = 'https://'+vm_sso+':7343/console/?vmId='+MOR_id+'&vmName='+vm_name+'&host='+i_host+'&sessionTicket='+sess_tkt+'&thumbprint='+ssl_tp
                webbrowser.open_new(url)
                retry = 5
                break
            else:
                print "crap,something is wrong"
                continue


if __name__ == "__main__":
    main()