import os
import sys
import subprocess
from datetime import datetime


class Tools:
    def __init__(self, nuclei_iserver="", nuclei_severity="high,critical", nuclei_templates_path=""):
        self.commands = ["nuclei"]
        self.iserver = ""
        self.eid = "" # TODO
        self.severity = nuclei_severity
        self.nuclei_templates_path = nuclei_templates_path

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

            cmd = ""

            if self.nuclei_templates_path != "":
                 if self.iserver != "":
                    cmd = ['nuclei', '-l', file_new_subdomains, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', 'high,critical', '-iserver', self.iserver]
                 if self.iserver != "" and self.severity != "high,critical":
                    cmd = ['nuclei', '-l', file_new_subdomains, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', self.severity, '-iserver', self.iserver]
                 if self.iserver == "":
                    cmd = ['nuclei', '-l', file_new_subdomains, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', 'high,critical']
                 

            if self.iserver != "":
                cmd = ['nuclei', '-l', file_new_subdomains, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-t', '/root/nuclei-templates/http/takeovers', '-o', 'nuclei_results.txt', '-s', 'high,critical', '-iserver', self.iserver]
            
            if self.iserver != "" and self.severity != "high,critical":
                cmd = ['nuclei', '-l', file_new_subdomains, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-t', '/root/nuclei-templates/http/takeovers', '-o', 'nuclei_results.txt', '-s', self.severity, '-iserver', self.iserver]

            if self.iserver == "":
                cmd = ['nuclei', '-l', "new_subdomains.txt", '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration','-t','/root/nuclei-templates/http/takeovers' '-o', 'nuclei_results.txt', '-s','high,critical']

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
        cmd = ""

        if self.nuclei_templates_path != "":
                 if self.iserver != "":
                    cmd = ['nuclei', '-u', domain, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', 'high,critical', '-iserver', self.iserver]
                 if self.iserver != "" and self.severity != "high,critical":
                    cmd = ['nuclei', '-u', domain, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', self.severity, '-iserver', self.iserver]
                 if self.iserver == "":
                    cmd = ['nuclei', '-u', domain, '-t', self.nuclei_templates_path, '-o', 'nuclei_results.txt', '-s', 'high,critical']

        if self.iserver != "":
            cmd = ['nuclei', '-u', domain, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-t', '/root/nuclei-templates/http/takeovers', '-o', 'nuclei_results.txt', '-s', 'high,critical', '-iserver', self.iserver]
        
        if self.iserver != "" and self.severity != "high,critical":
            cmd = ['nuclei', '-u', domain, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration', '-t', '/root/nuclei-templates/http/takeovers', '-o', 'nuclei_results.txt', '-s', self.severity, '-iserver', self.iserver]
            
        if self.iserver == "":
            cmd = ['nuclei', '-u', domain, '-t', '/root/nuclei-templates/http/cves', '-t', '/root/nuclei-templates/http/misconfiguration','-t','/root/nuclei-templates/http/takeovers' '-o', 'nuclei_results.txt', '-s','high,critical']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if os.path.isfile('nuclei_results.txt'):
                print(f"File 'nuclei_results.txt' sent to Telegram {current_time}")
                return os.path.abspath('nuclei_results.txt')
        except Exception as e:
                print(f"Error encountered: {e}")
                return None
