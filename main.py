
import os
import sys
import os
import argparse
from dotenv import load_dotenv
from Utils import WildCard
from sender import Telegram
from certsh import Database
from Utils import Tools
import time
import subprocess

menu = argparse.ArgumentParser(description="Submon - A tool to find subdomains and certificates and monitor them for changes.")
menu.add_argument("-f", "--file", help="file with domains to monitor", required=False, default="domains.txt")
menu.add_argument("-d", "--delete", help="delete a domain and its subdomains from the database", required=False, default=None)
menu.add_argument("-l", "--list", help="list all domains in the database", required=False, action="store_true")
menu.add_argument("-ls", "--listsub", help="list all subdomains for a domain", required=False, default=None)
menu.add_argument("-sd", "--singledomain", help="check a single domain", required=False, default=None)
menu.add_argument("-n", "--nuclei", help="run nuclei on the new subdomains", required=False, action="store_true") ## TODO improve this
menu.add_argument("-is", "--iserver", help="run nuclei on the new subdomains", required=False, default=None)
menu.add_argument("-se", "--severity", help="run nuclei on the new subdomains", required=False, default="high,critical")
args = menu.parse_args()

if len(sys.argv) < 1:
    menu.print_help()
    print("Usage: python3 main.py -f domains.txt")
    sys.exit(1)

domains_file = args.file
delete_domain = args.delete
list_domains = args.list
run_nuclei = args.nuclei
list_subdomains = args.listsub
single_domain = args.singledomain
nuclei_iserver = args.iserver
nuclei_severity = args.severity

if domains_file == "" and single_domain == None:
    print("You must specify a file with domains to monitor or a single domain to check.")
    menu.print_help()
    sys.exit(1)


if not os.path.isfile(domains_file):
    print(f"File '{domains_file}' not found.")
    sys.exit(1)

if delete_domain:
    cert_obj = Database.CertDatabase()
    cert_obj.delete_domain_and_subdomains(delete_domain)
    sys.exit(0)

if list_subdomains:
    print(f"[*] Listing all subdomains in the database from domain: {list_subdomains}")
    cert_obj = Database.CertDatabase()
    domains = cert_obj.list_subdomains_for_domain(list_subdomains)
    if len(domains) < 1:
        print(f"[*] No subdomains found for domain: {list_subdomains}")
        sys.exit(0)
    for domain in domains:
        print(domain)
    sys.exit(0)

if list_domains:
    cert_obj = Database.CertDatabase()
    domains = cert_obj.list_all_domains()
    for domain in domains:
        print(domain)

def main():
    load_dotenv()
    TOKEN = os.getenv("API_TOKEN_TELEGRAM")
    CHAT = os.getenv("CHAT_ID")
    current_time = time.ctime()
    cert_obj = Database.CertDatabase()
    wild_card_obj = WildCard.WildCardFilter()
    telegram = Telegram.Telegram(TOKEN, CHAT)

    if delete_domain:
        cert_obj = Database.CertDatabase()
        cert_obj.delete_domain_and_subdomains(delete_domain)
        sys.exit(0)

    if list_domains:
        cert_obj = Database.CertDatabase()
        domains = cert_obj.list_all_domains()
        for domain in domains:
            print(domain)
        sys.exit(0)

    if args.singledomain:
        single_domain = args.singledomain
        print(f"[*] Checking domain: {single_domain}")
        if not wild_card_obj.is_wildcard_domain(single_domain):
            single_domain = single_domain.strip()
        results = cert_obj.monitor_single_domain(single_domain)
        if len(results) == 0:
            print(f"[*] No subdomains found for domain: {single_domain}")
            sys.exit(0)
        else:
            if len(results) > 20:
                file_write = f"{single_domain}_subdomains.txt"
                with(open(file_write, 'w')) as file:
                    for line in results:
                        file.write(f"{line}\n")
                
                telegram.send(f"📦 New subdomains from {single_domain} found. See attached file. {current_time}")
                telegram.send_file(file_write)
                new_subdomains = cert_obj.get_new_subdomains_to_notify()
                cert_obj.mark_subdomains_as_notified(new_subdomains)
                if run_nuclei:
                    print(f"[*] Running nuclei on the new subdomains")
                    tools_obj = Tools.Tools()
                    tools_obj.check_tools()
                    file_new_subdomains = os.path.abspath(file_write)
                    tools_obj.run_nuclei(file_new_subdomains)
                    print(f"[*] Nuclei scan completed")
                    if os.path.isfile('nuclei_results.txt'):
                        telegram.send_file('nuclei_results.txt')
                        print(f"[*] File 'nuclei_results.txt' sent to Telegram {current_time}")
                        os.remove('nuclei_results.txt')
                        os.remove(file_write)
            else:
                for line in results:
                    template_telegram = f"🧙🏻‍♂️ New subdomain found: {line}\n{current_time}\n"
                    telegram.send(template_telegram)
                    new_subdomains = cert_obj.get_new_subdomains_to_notify()
                    cert_obj.mark_subdomains_as_notified(new_subdomains)
                    if run_nuclei:
                        print(f"[*] Running nuclei on the new subdomains")
                        tools_obj = Tools.Tools()
                        tools_obj.check_tools()
                        tools_obj.run_single_nuclei(line)
                        print(f"[*] Nuclei scan completed")
                        if os.path.isfile('nuclei_results.txt'):
                            telegram.send_file('nuclei_results.txt')
                            print(f"[*] Scan completed for {line} and sent to Telegram {current_time}")
                            os.remove('nuclei_results.txt')
                            os.remove(file_write)
    if domains_file:
        file_path = os.path.abspath(domains_file)
        with open(file_path, 'r') as file:
            for domain in file.readlines():
                # filter wildcard subdomains
                print(f"[*] Checking domain: {domain}")
                if not wild_card_obj.is_wildcard_domain(domain):
                    domain = domain.strip()
                results = cert_obj.lookup(domain)
        for result in results:
            print(result)
        new_subdomains = cert_obj.get_new_subdomains_to_notify()
        if new_subdomains:
            if len(new_subdomains) > 20:
                telegram.send(f"📦 New subdomains found. See attached file. {current_time}")
                with open('new_subdomains.txt', 'a') as file:
                    for line in new_subdomains:
                        file.write(f"{line}\n")
                telegram.send_file('new_subdomains.txt')
                print(f"File 'new_subdomains.txt' sent to Telegram {current_time}")
                if run_nuclei:
                    print(f"[*] Running nuclei on the new subdomains")
                    tools_obj = Tools.Tools()
                    tools_obj.check_tools()
                    file_new_subdomains = os.path.abspath('new_subdomains.txt')
                    tools_obj.run_nuclei(file_new_subdomains)
                    print(f"[*] Nuclei scan completed")
                    if os.path.isfile('nuclei_results.txt'):
                        telegram.send_file('nuclei_results.txt')
                        print(f"[*] File 'nuclei_results.txt' sent to Telegram {current_time}")
                        os.remove('nuclei_results.txt')
                os.remove('new_subdomains.txt') ## if you want to keep the file comment this line 
                cert_obj.mark_subdomains_as_notified(new_subdomains)
            else:
                for line in new_subdomains:
                    template_telegram = f"🧙🏻‍♂️ New subdomain found: {line}\n{current_time}\n"
                    telegram.send(template_telegram)
                    cert_obj.mark_subdomains_as_notified(new_subdomains)
        

if __name__ == "__main__":
    main()
