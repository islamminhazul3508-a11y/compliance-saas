import subprocess
import os
import time
from datetime import datetime, timezone

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def process_target(domain):
    print(f"\n" + "=" * 50)
    print(f"[*] Processing Target: {domain}")
    print("=" * 50)

    # 1. Asset Mapping
    success, out, err = run_cmd(f"python asset_mapper.py {domain}")
    if not success:
        print(f"[-] Asset mapping failed for {domain}: {err}")
        return

    # 2. Drift Detection
    run_cmd("python drift_detector.py")

    # 3. Compliance Scoring
    run_cmd("python compliance_scorer.py")

    # 4. Report Generation
    run_cmd("python report_generator.py")

    # 5. Archive Report for Client
    reports_dir = "client_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_filename = f"{reports_dir}/{domain}_{timestamp}_report.md"
    
    if os.path.exists("audit_report.md"):
        os.rename("audit_report.md", archive_filename)
        print(f"[+] Client Report Archived: {archive_filename}")

def main():
    if not os.path.exists("targets.txt"):
        print("[-] targets.txt not found. Create it with target domains.")
        return

    with open("targets.txt", "r") as f:
        targets = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not targets:
        print("[-] targets.txt is empty.")
        return

    print(f"[+] Starting Batch Engine for {len(targets)} client targets...")

    for domain in targets:
        process_target(domain)
        time.sleep(2)

    print("\n" + "=" * 50)
    print("[+] ALL TARGETS PROCESSED SUCCESSFULLY")
    print("[+] Check folder: client_reports/")
    print("=" * 50)

if __name__ == "__main__":
    main()
