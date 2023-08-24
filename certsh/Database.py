import json
import psycopg2
import requests
requests.packages.urllib3.disable_warnings()
import re
import sqlite3
from Resolv import Dnss

DB_HOST = 'crt.sh'
DB_NAME = 'certwatch'
DB_USER = 'guest'
DB_PASSWORD = ''


class CertDatabase:
    """Connects to crt.sh public API to retrieve subdomains."""

    def __init__(self, enable_logging=True, db_path="domains.db"):
        self.enable_logging = enable_logging
        self.db_path = db_path
        self._initialize_db()
        self.dns_obj = Dnss.Dnss()

    def _log(self, msg):
        if self.enable_logging:
            print(msg)

    def monitor_single_domain(self, domain):
        # Fetch subdomains from crt.sh
        subdomains = self.lookup(domain)
        
        # Resolve and filter subdomains
        resolved_subdomains = self.dns_obj.dns_resolution(subdomains)
        
        # Save to SQLite database
        self._save_to_db(domain, resolved_subdomains)

        return resolved_subdomains

    def _get_subdomains_from_db(self, domain):
        unique_domains = set()
        try:
            with psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    query = ("SELECT ci.NAME_VALUE FROM certificate_identity ci "
                             "WHERE ci.NAME_TYPE = 'dNSName' AND reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower(%s));")
                    cursor.execute(query, [f"%{domain}"])
                    for result in cursor.fetchall():
                        matches = re.findall(r"\'(.+?)\'", str(result))
                        for subdomain in matches:
                            try:
                                if get_fld(f"https://{subdomain}") == domain:
                                    unique_domains.add(subdomain.lower())
                            except Exception as e:
                                self._log(f"Error processing subdomain {subdomain}: {e}")
        except Exception as e:
            self._log(f"Error fetching subdomains from database: {e}")
        return sorted(unique_domains)

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

        # Create domains table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL
            );
        """)

        # Create subdomains table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subdomains (
                id INTEGER PRIMARY KEY,
                domain_id INTEGER,
                subdomain TEXT NOT NULL,
                notified BOOLEAN DEFAULT 0,
                FOREIGN KEY(domain_id) REFERENCES domains(id),
                UNIQUE(domain_id, subdomain)
            );
        """)
            conn.commit()


    def _get_subdomains_from_api(self, domain):
        base_url = "https://crt.sh/?q={}&output=json"
        subdomains = set()
        try:
            if domain.startswith("%25."):
                url = base_url.format(domain)
            else:
                url = base_url.format(f"%25.{domain}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0'
            }
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = json.loads(response.content.decode('utf-8'))
                for subdomain in data:
                    subdomains.add(subdomain["name_value"].lower())
        except Exception as e:
            self._log(f"Error fetching subdomains from API: {e}")
        return sorted(subdomains)

    def _save_to_db(self, domain, subdomains):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if domain exists
            cursor.execute("SELECT id FROM domains WHERE domain=?", (domain,))
            domain_id = cursor.fetchone()
            if not domain_id:
                cursor.execute("INSERT INTO domains (domain) VALUES (?)", (domain,))
                conn.commit()  # commit after inserting to make sure the row is created
                domain_id = cursor.lastrowid
            else:
                domain_id = domain_id[0]

            # For each subdomain, check if it exists for the specific domain and save if it doesn't
            for subdomain in subdomains:
                cursor.execute("SELECT id FROM subdomains WHERE subdomain=? AND domain_id=?", (subdomain, domain_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO subdomains (domain_id, subdomain) VALUES (?, ?)", (domain_id, subdomain))

            conn.commit()  # commit all changes at the end

    def list_subdomains_for_domain(self, domain):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Fetch the id of the domain
            cursor.execute("SELECT id FROM domains WHERE domain=?", (domain,))
            domain_id = cursor.fetchone()

            if domain_id:
                domain_id = domain_id[0]

                # Fetch all subdomains associated with the domain_id
                cursor.execute("SELECT subdomain FROM subdomains WHERE domain_id=?", (domain_id,))
                subdomains = cursor.fetchall()

                # Return the list of subdomains
                return [sub[0] for sub in subdomains]
            else:
                print(f"Domain '{domain}' not found in the database.")
                return []



    def delete_domain_and_subdomains(self, domain):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            
            cursor.execute("SELECT id FROM domains WHERE domain=?", (domain,))
            domain_id = cursor.fetchone()

            if domain_id:
                domain_id = domain_id[0]

                # Delete all subdomains associated with that domain
                cursor.execute("DELETE FROM subdomains WHERE domain_id=?", (domain_id,))

            
                cursor.execute("DELETE FROM domains WHERE id=?", (domain_id,))

                conn.commit()

                print(f"Deleted domain '{domain}' and its associated subdomains from the database.")
            else:
                print(f"Domain '{domain}' not found in the database.")

    def list_all_domains(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Fetch all domains from the domains table
            cursor.execute("SELECT domain FROM domains")
            domains = cursor.fetchall()

            # Return the list of domains
            return [domain[0] for domain in domains]


    def resolve_and_save(self, domain, subdomains):
        resolved_subdomains = self.dns_obj.dns_resolution(subdomains)
        if resolved_subdomains:
            self._save_to_db(domain, resolved_subdomains)


    # TODO create new subomains to notify from single domain monitor

    def get_new_subdomains_to_notify(self):
        """Retrieve a list of subdomains that have not yet been notified."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subdomain FROM subdomains WHERE notified=0")
            results = cursor.fetchall()
            return [res[0] for res in results]
        
    def mark_subdomains_as_notified(self, subdomains):
        """Mark subdomains as notified."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("UPDATE subdomains SET notified=1 WHERE subdomain=?", [(sub,) for sub in subdomains])
            conn.commit()

    def lookup(self, domain, wildcard=True):
        domain = domain.replace('%25.', '')

        # First, try fetching from the database
        subdomains = self._get_subdomains_from_db(domain)

        # If failed, fetch from the public API
        if not subdomains:
            subdomains = self._get_subdomains_from_api(domain)
        
        self._save_to_db(domain, subdomains)

        return subdomains

