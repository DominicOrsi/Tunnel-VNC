'''
SSH Tunnel to VNC v0.1
Description: Creates an SSH Tunnel to connect to cloud instance
Requirements: Tiger VNC, SSL Private Key, Instance IP Address
Date: 09/29/23
By: Dominic Orsi
'''

import sshtunnel
import paramiko
import subprocess
import os

# Create logger
log = sshtunnel.create_logger(loglevel='DEBUG')

'''
Description: 
Input: remote_host, ssh_pkey_path
Output: server
'''
def createTunnel(remote_host, ssh_pkey_path):
    server = sshtunnel.SSHTunnelForwarder(
    (remote_host, 22),
    ssh_username='ubuntu',
    ssh_private_key=ssh_pkey_path,
    remote_bind_address=('localhost', 5901),
    local_bind_address=('0.0.0.0', 59000),
    logger=log,
    )

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser('~\\.ssh\known_hosts'))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.save_host_keys(os.path.expanduser('~\\.ssh\\known_hosts'))

    return server

'''
Description:
Input:
Output:
'''
def startServer(server):
    print('Server Starting')
    server.start()


'''
Description:
Input:
Output:
'''
def startTigerVNC(tiger_vnc_path):
    # Define powershell as list 
    powershell_command = [
        'powershell',
        'Start-Process',
        '-FilePath',
        f'\"{tiger_vnc_path}\"',
        '-ArgumentList',
        '"127.0.0.1:59000"'
    ]
    subprocess.run(powershell_command, check=True)

def stopServer(server):
    print('Server connection closing')
    server.close()