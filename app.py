from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import os

app = Flask(__name__)

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Security & Compliance Portal</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }
        .container { max-width: 650px; margin: 30px auto; background: #161b22; padding: 25px; border-radius: 8px; border: 1px solid #30363d; }
        h1 { color: #58a6ff; font-size: 22px; text-align: center; }
        p { font-size: 14px; color: #8b949e; text-align: center; }
        input[type="text"] { width: 100%; padding: 12px; margin: 15px 0; background: #0d1117; border: 1px solid #30363d; color: #fff; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #238636; border: none; color: #fff; font-weight: bold; border-radius: 6px; cursor: pointer; }
        button:hover { background: #2ea043; }
        .result-card { margin-top: 20px; padding: 15px; border-radius: 6px; background: #0d1117; border: 1px solid #30363d; display: none; }
        .score { font-size: 26px; font-weight: bold; }
        .grade-a { color: #3fb950; }
        .grade-f { color: #f85149; }
        .btn-pay { display: inline-block; margin-top: 15px; padding: 10px 20px; background: #1f6feb; color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Autonomous Asset & Compliance Portal</h1>
        <p>SOC 2 & ISO 27001 Real-Time Surface Verification</p>
        <input type="text" id="domain" placeholder="Enter Domain (e.g. secure-enterprise.com)" />
        <button onclick="runAudit()">Run Security Audit</button>
        
        <div id="result" class="result-card"></div>
    </div>

    <script>
        async function runAudit() {
            const domain = document.getElementById('domain').value.trim();
            if(!domain) { alert('Please enter a domain.'); return; }
            
            const resultCard = document.getElementById('result');
            resultCard.style.display = 'block';
            resultCard.innerHTML = '<p>Auditing surface and DNS infrastructure... Please wait.</p>';

            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({domain: domain})
                });
                const data = await response.json();
                
                let gradeClass = data.compliance_score >= 85 ? 'grade-a' : 'grade-f';
                let html = `<div class="score ${gradeClass}">Score: ${data.compliance_score}/100 (${data.grade})</div>`;
                html += `<p style="text-align:left; color:#c9d1d9; margin-top:10px;">Target: <b>${data.domain}</b></p>`;
                
                if(data.findings && data.findings.length > 0) {
                    html += '<ul style="text-align:left; color:#f85149;">';
                    data.findings.forEach(f => { html += `<li>${f}</li>`; });
                    html += '</ul>';
                } else {
                    html += '<p style="text-align:left; color:#3fb950;">All compliance controls verified. Zero critical drift.</p>';
                }
                
                html += `<hr style="border: 0; border-top: 1px solid #30363d; margin: 15px 0;">
                        <div style="text-align: center;">
                            <p style="margin-bottom: 10px;">Continuous 24/7 Monitoring & Drift Protection</p>
                            <a href="https://buy.stripe.com/test_placeholder" target="_blank" class="btn-pay">Subscribe - $600 / Month</a>
                        </div>`;
                
                resultCard.innerHTML = html;
            } catch(e) {
                resultCard.innerHTML = '<p style="color:#f85149;">Error running audit pipeline.</p>';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def dashboard():
    return render_template_string(HTML_PAGE)

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json(silent=True) or {}
    domain = data.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain cannot be empty"}), 400

    run_cmd(f"python asset_mapper.py {domain}")
    run_cmd("python drift_detector.py")
    run_cmd("python compliance_scorer.py")
    run_cmd("python report_generator.py")

    score_path = "compliance_score.json"
    if os.path.exists(score_path):
        with open(score_path, "r") as f:
            return jsonify(json.load(f))

    return jsonify({"error": "Audit failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
