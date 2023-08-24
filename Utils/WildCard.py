import dns.resolver
import random
import string

class WildCardFilter:
    def __init__(self) -> None:
        pass

    def random_subdomain(self, length=8):
        """Generate a random subdomain of the given length."""
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    def is_wildcard_domain(self, domain):
        # Generate two random subdomains
        sub1 = f"{self.random_subdomain()}.{domain}"
        sub2 = f"{self.random_subdomain()}.{domain}"

        try:
            # Resolving the IP addresses for the subdomains
            ip1 = dns.resolver.resolve(sub1, 'A')[0].address
            ip2 = dns.resolver.resolve(sub2, 'A')[0].address

           
            if ip1 == ip2:
                print(f"Both {sub1} and {sub2} resolve to {ip1}. This domain might be a wildcard domain.")
                return True
            else:
                print(f"{sub1} resolves to {ip1} and {sub2} resolves to {ip2}. This domain is likely not a wildcard domain.")
                return False
        except dns.resolver.NXDOMAIN:
            print("Subdomains do not resolve. This domain is not a wildcard domain.")
            return False
        except Exception as e:
            print(f"Error encountered: {e}")
            return False
