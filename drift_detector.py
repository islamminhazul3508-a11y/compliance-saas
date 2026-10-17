import json
import os
from datetime import datetime, timezone

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def detect_drift(baseline, current):
    changes = {
        "domain": current.get("domain"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dns_drift": {},
        "security_header_drift": {},
        "has_critical_drift": False
    }

    # 1. DNS Drift Check
    base_dns = baseline.get("dns_records", {})
    curr_dns = current.get("dns_records", {})

    for rtype in ["A", "AAAA", "CNAME", "MX", "TXT"]:
        b_records = set(base_dns.get(rtype, []))
        c_records = set(curr_dns.get(rtype, []))

        added = list(c_records - b_records)
        removed = list(b_records - c_records)

        if added or removed:
            changes["dns_drift"][rtype] = {
                "added": added,
                "removed": removed
            }
            changes["has_critical_drift"] = True

    # 2. Security Headers Drift Check
    base_headers = baseline.get("web_security", {}).get("security_headers", {})
    curr_headers = current.get("web_security", {}).get("security_headers", {})

    for header, status in base_headers.items():
        curr_status = curr_headers.get(header)
        if status != curr_status:
            changes["security_header_drift"][header] = {
                "previous_state": status,
                "current_state": curr_status
            }
            if curr_status is False:
                changes["has_critical_drift"] = True

    return changes

def run():
    baseline = load_json("baseline_assets.json")
    current = load_json("current_assets.json")

    if not baseline or not current:
        print("[-] Baseline or Current assets file missing.")
        return

    report = detect_drift(baseline, current)

    with open("drift_alerts.json", "w") as f:
        json.dump(report, f, indent=4)

    if report["has_critical_drift"]:
        print("[!] ALERT: Security/Asset Drift detected! Check drift_alerts.json")
    else:
        print("[+] No Drift Detected. Infrastructure is synchronized with baseline.")

if __name__ == "__main__":
    run()
