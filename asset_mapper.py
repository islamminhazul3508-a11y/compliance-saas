import dns.resolver
import requests
import json
import sys
from datetime import datetime, timezone

class AssetMapper:
    def __init__(self, domain):
        self.domain = domain
        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        self.resolver.timeout = 3.0
        self.resolver.lifetime = 3.0

    def get_dns_records(self):
        records = {}
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT']
        
        for rtype in record_types:
            try:
                answers = self.resolver.resolve(self.domain, rtype)
                records[rtype] = [str(r.to_text()).strip('"') for r in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                records[rtype] = []
            except Exception as e:
                records[rtype] = [f"Error: {str(e)}"]
                
        return records

    def inspect_http_security(self):
        target_url = f"https://{self.domain}"
        http_data = {
            "url": target_url,
            "status_code": None,
            "security_headers": {
                "Strict-Transport-Security": False,
                "Content-Security-Policy": False,
                "X-Frame-Options": False,
                "X-Content-Type-Options": False
            }
        }
        
        try:
            response = requests.get(target_url, timeout=5, allow_redirects=True)
            http_data["status_code"] = response.status_code
            headers = response.headers
            
            for header in http_data["security_headers"]:
                if header in headers:
                    http_data["security_headers"][header] = True
        except requests.exceptions.RequestException as e:
            http_data["error"] = str(e)
            
        return http_data

    def run_discovery(self):
        print(f"[*] Scanning assets for: {self.domain}")
        dns_data = self.get_dns_records()
        http_data = self.inspect_http_security()
        
        result = {
            "domain": self.domain,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dns_records": dns_data,
            "web_security": http_data
        }
        
        output_file = "current_assets.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=4)
            
        print(f"[+] Scan complete. Data saved to {output_file}")
        return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_domain = sys.argv[1].strip()
    else:
        target_domain = input("Enter authorized target domain (e.g. example.com): ").strip()

    if target_domain:
        mapper = AssetMapper(target_domain)
        mapper.run_discovery()
    else:
        print("[-] Domain cannot be empty.")
