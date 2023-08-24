import os
import sys
import subprocess
from datetime import datetime


class Tools:
    def __init__(self):
        self.commands = ["nuclei"]
        self.iserver = ""
        self.severity = ""

    def check_tools(self):
        for command in self.commands:
            if os.system(f"which {command} > /dev/null") != 0:
                print(f"{command} not found")
                sys.exit(1)

    def run_nuclei(self, file_new_subdomains):
        if not os.path.isfile(file_new_subdomains):
                print(f"File '{file_new_subdomains} not found.")
                return
        else:
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            cmd = ['nuclei', '-l', "new_subdomains.txt", '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-o', 'nuclei_results.txt', '-iserver', 'ckbr1p62vtc0000994w0gj3itnayyyyyn.osoro.zip', '-s' , 'high,critical']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if os.path.isfile('nuclei_results.txt'):
                    print(f"File 'nuclei_results.txt' sent to Telegram {current_time}")
                    return os.path.abspath('nuclei_results.txt')
            except Exception as e:
                    print(f"Error encountered: {e}")
                    return None
    
    def run_single_nuclei(self, domain):
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cmd = ['nuclei', '-u', domain, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-o', 'nuclei_results.txt', '-iserver', 'ckbr1p62vtc0000994w0gj3itnayyyyyn.osoro.zip', '-s' , 'high,critical']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if os.path.isfile('nuclei_results.txt'):
                print(f"File 'nuclei_results.txt' sent to Telegram {current_time}")
                return os.path.abspath('nuclei_results.txt')
        except Exception as e:
                print(f"Error encountered: {e}")
                return None
        
    # TODO subdomain takeover :P
