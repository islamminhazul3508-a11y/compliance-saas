import json
import os
from datetime import datetime, timezone

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def calculate_score(assets, drift):
    score = 100
    deductions = []

    web_sec = assets.get("web_security", {})
    headers = web_sec.get("security_headers", {})
    
    header_weights = {
        "Strict-Transport-Security": 15,
        "Content-Security-Policy": 15,
        "X-Frame-Options": 5,
        "X-Content-Type-Options": 5
    }

    for header, weight in header_weights.items():
        if not headers.get(header, False):
            score -= weight
            deductions.append(f"Missing {header} (-{weight} pts) [SOC 2 CC6.6]")

    if drift and drift.get("has_critical_drift", False):
        score -= 30
        deductions.append("Critical Asset/DNS Drift Detected (-30 pts) [ISO 27001 A.12.1.2]")

    dns_records = assets.get("dns_records", {})
    txt_records = " ".join(dns_records.get("TXT", []))
    
    if "v=spf1" not in txt_records:
        score -= 15
        deductions.append("Missing SPF record (-15 pts) [Email Spoofing Risk]")
    
    final_score = max(0, score)
    
    if final_score == 100:
        grade = "A+"
    elif final_score >= 85:
        grade = "A"
    elif final_score >= 70:
        grade = "B"
    elif final_score >= 50:
        grade = "C"
    else:
        grade = "F"

    return {
        "domain": assets.get("domain"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compliance_score": final_score,
        "grade": grade,
        "frameworks": ["SOC 2 Type II", "ISO 27001:2022"],
        "findings": deductions
    }

def run():
    assets = load_json("current_assets.json")
    drift = load_json("drift_alerts.json")

    if not assets:
        print("[-] current_assets.json not found.")
        return

    compliance_report = calculate_score(assets, drift)

    with open("compliance_score.json", "w") as f:
        json.dump(compliance_report, f, indent=4)

    print(f"[+] Assessment Complete.")
    print(f"[*] Target: {compliance_report['domain']}")
    print(f"[*] Security Score: {compliance_report['compliance_score']}/100 (Grade: {compliance_report['grade']})")
    print(f"[*] Findings recorded: {len(compliance_report['findings'])}")

if __name__ == "__main__":
    run()
