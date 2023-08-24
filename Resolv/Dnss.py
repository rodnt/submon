import dns.resolver
import dns.exception


class Dnss:
    def __init__(self) -> None:
        pass

    def dns_resolution(new_subdomains): 
        dns_results = {}
        resolved_subdomains = set()
        subdomains_to_resolve = new_subdomains

        print("\n[!] Performing DNS resolution. Please do not interrupt!")

        for domain in subdomains_to_resolve:
            domain = domain.replace('+ ','').replace('*.','')
            dns_results[domain] = {}

            for qtype in ['A','CNAME', 'MX', 'TXT', 'NS']: 
                try:
                    dns_output = dns.resolver.query(domain, qtype, raise_on_no_answer = False)
                    if dns_output.rrset:
                        if qtype == 'A':
                            dns_results[domain]["A"] = [str(i) for i in dns_output.rrset]
                        elif qtype == 'CNAME':
                            dns_results[domain]["CNAME"] = [str(i) for i in dns_output.rrset]
                        elif qtype == 'MX':
                            dns_results[domain]["MX"] = [str(i) for i in dns_output.rrset]
                        elif qtype == 'TXT':
                            dns_results[domain]["TXT"] = [str(i) for i in dns_output.rrset]
                        elif qtype == 'NS':
                            dns_results[domain]["NS"] = [str(i) for i in dns_output.rrset]
                except dns.resolver.NXDOMAIN:
                    pass
                except dns.resolver.Timeout:
                    dns_results[domain]["A"] = ["Timed out while resolving."]
                    dns_results[domain]["CNAME"] = ["Timed out error while resolving."]
                    with open('error_log.txt', 'a') as log_file:
                        log_file.write(f"Timeout error for domain: {domain}\n")
                except dns.exception.DNSException as e:
                    dns_results[domain]["A"] = ["There was an error while resolving."]
                    dns_results[domain]["CNAME"] = ["There was an error while resolving."]
                    with open('error_log.txt', 'a') as log_file:
                        log_file.write(f"DNS error for domain {domain}: {e}\n")

        if dns_results:
            if domain in dns_results and dns_results[domain]:
                resolved_subdomains.add(domain)
                return list(resolved_subdomains)
        else:
            return None
