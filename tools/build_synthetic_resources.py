from __future__ import annotations

from html import escape
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "resources"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

STYLE = """
@page { size: letter; margin: .62in; }
* { box-sizing: border-box; }
body { color:#17263a; font: 10pt/1.45 Arial, sans-serif; margin:0; }
a { color:#0d5b85; text-decoration:underline; }
h1 { color:#173853; font-size:24pt; margin:0 0 8pt; }
h2 { color:#1b6d67; font-size:15pt; margin:0 0 8pt; }
h3 { color:#173853; font-size:11pt; margin:12pt 0 4pt; }
p { margin:4pt 0 8pt; }
.eyebrow { color:#327e78; font-size:8pt; font-weight:bold; letter-spacing:1.4pt; text-transform:uppercase; }
.banner { border:2px solid #a84f58; background:#fff2f2; color:#812e39; padding:9pt 12pt; font-weight:bold; margin:12pt 0; }
.note { border-left:4px solid #55bba5; background:#eff9f7; padding:8pt 11pt; margin:9pt 0; }
.small { color:#596b7e; font-size:8pt; }
.line { border-bottom:1px solid #8794a0; height:22pt; }
.field { margin:9pt 0; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:8pt 18pt; }
.check { display:inline-block; width:11px; height:11px; border:1px solid #566879; margin-right:5px; vertical-align:-1px; }
.box { border:1px solid #a8b5c1; min-height:48pt; margin:5pt 0 12pt; }
.box.large { min-height:130pt; }
table { border-collapse:collapse; width:100%; margin:8pt 0; }
th { background:#eaf1f7; text-align:left; color:#183750; }
th,td { border:1px solid #aeb9c4; padding:5pt 6pt; vertical-align:top; }
.page { break-after:page; }
.page:last-child { break-after:auto; }
.footer { color:#667689; font-size:7pt; border-top:1px solid #d8e0e7; padding-top:4pt; }
.compact { font-size:8.5pt; line-height:1.25; }
.compact h1 { font-size:20pt; margin-bottom:5pt; }
.compact h2,.compact h3 { margin:7pt 0 4pt; }
.compact p { margin:3pt 0 5pt; }
.compact .field { margin:4pt 0; }
.compact .line { height:16pt; }
.compact .box { min-height:34pt; margin:3pt 0 6pt; }
.compact .box.large { min-height:85pt; }
.compact .banner,.compact .note { margin:6pt 0; padding:6pt 9pt; }
"""


def page(content: str) -> str:
    return f'<section class="page">{content}</section>'


def html_doc(title: str, body: str, compact: bool = False) -> str:
    css_class = " class=\"compact\"" if compact else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{escape(title)}</title><style>{STYLE}</style></head>
<body{css_class}><div class="footer">Synthetic development resource · Not CDIT policy · Do not submit real personal or health information to this local prototype</div>{body}</body></html>"""


policy = "".join([
    page('<div class="eyebrow">ActionRelay resource library</div><h1>Workplace Guide</h1><h2>Synthetic sample booklet</h2><div class="banner">SYNTHETIC SAMPLE — NOT ACTUAL CDIT COMPANY POLICY</div><p>This short example shows how a general workplace guide might be organized. It is fictional development content and does not set real employment rules, benefits, deadlines, or eligibility.</p><div class="note"><b>For real policies:</b> ask your supervisor or Human Resources for the current employer-approved handbook and process.</div><h3>In this sample</h3><ol><li>Respectful workplace</li><li>Time away and leave questions</li><li>Timekeeping and payroll questions</li><li>Technology, privacy, and reporting concerns</li></ol><p class="small">Version: synthetic sample 1.0 · Prepared for interface demonstration.</p>'),
    page('<div class="eyebrow">Section 1</div><h1>Respectful workplace</h1><p>Employees should communicate respectfully, protect confidential information, and use established channels to raise workplace concerns. This section is a fictional example, not an enforceable policy.</p><h3>Everyday expectations</h3><ul><li>Treat coworkers and visitors professionally.</li><li>Use approved systems for work communications and records.</li><li>Ask a supervisor or HR when a process is unclear.</li><li>Report urgent safety or security concerns through the employer’s designated channel.</li></ul><div class="note">This sample does not replace a real anti-harassment, accommodation, safety, or conduct policy.</div><h3>Where to ask</h3><p>Routine work questions: Supervisor or Staff Helpdesk.</p><p>Workplace conduct or accommodation questions: Human Resources.</p><p>Use the verified internal contact directory supplied by the employer.</p>'),
    page('<div class="eyebrow">Section 2</div><h1>Time away and leave</h1><p>For ordinary vacation or schedule requests, use the employer’s approved request process and contact your supervisor or HR. A request form is not an approval.</p><p>For a possible FMLA or New York Paid Family Leave request, contact HR before completing a form so the correct process and forms can be identified for your situation.</p><div class="note"><b>Supporting information varies.</b> HR or the relevant leave administrator should tell you what is needed. A health-care-provider certification may be requested for qualifying FMLA leave. Do not send full medical records or extra identity documents unless the authorized department specifically requests them.</div><p>Eligibility and approval decisions are made by the responsible employer or insurance administrator, not by this sample booklet or the support assistant.</p><h3>Potential documents, only when requested</h3><ul><li>Employee identifier needed to match the request</li><li>Applicable leave certification completed by the provider</li><li>Relationship or event documentation when the process requires it</li><li>Other documents specifically identified by HR or the insurer</li></ul>'),
    page('<div class="eyebrow">Section 3</div><h1>Timekeeping and payroll</h1><p>Review time entries and pay statements through the employer’s approved payroll system. If hours, deductions, or withholding appear incorrect, contact Payroll promptly and provide only the information Payroll requests through its approved channel.</p><p>The official IRS Form W-4 is available in the resource library for employees who need a blank federal withholding certificate. A personal W-2 or completed W-4 contains sensitive information and should go directly to Payroll through the employer-approved secure process.</p><div class="banner">This synthetic prototype does not accept or transmit real payroll records.</div><p>Do not include Social Security numbers, bank details, tax forms, or unredacted pay statements in general support tickets.</p>'),
    page('<div class="eyebrow">Section 4</div><h1>Technology, privacy, and reporting</h1><p>Use organization-approved devices and channels. Report suspected account compromise, unintended disclosure, or security incidents promptly to the authorized support or security contact.</p><p>Submit a complaint through the employer’s designated HR channel. Include relevant facts and dates, but avoid adding sensitive personal or medical details unless the authorized reviewer requests them through a protected process.</p><div class="note"><b>Prototype notice:</b> the local ActionRelay build uses synthetic demonstration records. Its document-upload control is not connected to a real HR, Payroll, or leave department. Never attach real personal documents to this prototype.</div><p>For current employer rules or a real report, contact the employer directly. This fictional guide must not be treated as legal advice, a benefits determination, or official company policy.</p>'),
])

names = [
    ("Avery Sample", "Supervisor", "avery.supervisor@example.com", "(212) 555-0101"),
    ("Jordan Example", "Supervisor", "jordan.supervisor@example.com", "(212) 555-0102"),
    ("Casey Demo", "Assistant Manager", "casey.assistantmanager@example.com", "(212) 555-0103"),
    ("Riley Sample", "Manager", "riley.manager@example.com", "(212) 555-0104"),
    ("Morgan Example", "Deputy Director", "morgan.deputydirector@example.com", "(212) 555-0105"),
    ("Taylor Demo", "Director", "taylor.director@example.com", "(212) 555-0106"),
    ("Quinn Sample", "Executive Director", "quinn.executivedirector@example.com", "(212) 555-0107"),
    ("Drew Example", "Auditor", "drew.auditor@example.com", "(212) 555-0108"),
    ("Skyler Demo", "Human Resources", "skyler.hr@example.com", "(212) 555-0109"),
    ("Reese Sample", "General HR", "hr@example.com", "(212) 555-0110"),
    ("Rowan Example", "Payroll", "rowan.payroll@example.com", "(212) 555-0111"),
    ("Finley Demo", "General Payroll", "payroll@example.com", "(212) 555-0112"),
    ("Alex Sample", "Staff Helpdesk", "helpdesk@example.com", "(212) 555-0113"),
]
rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(map(escape, row)) for row in names)
directory = "".join([
    page('<div class="eyebrow">ActionRelay resource library</div><h1>Company Directory</h1><h2>Fictional contacts for demonstration</h2><div class="banner">EVERY NAME, TITLE, EMAIL ADDRESS, AND PHONE NUMBER BELOW IS SYNTHETIC. DO NOT CONTACT.</div><p class="small">Email addresses use the reserved example.com domain. Phone numbers use fictional 555-01xx numbers.</p><table><thead><tr><th>Synthetic name</th><th>Supervisory / support title</th><th>Synthetic email</th><th>Fictional phone</th></tr></thead><tbody>'+rows+'</tbody></table><div class="note">This directory is a sample catalog only. It does not identify actual CDIT employees, actual departments, or working contacts.</div>'),
    page('<div class="eyebrow">Resource index</div><h1>Available Forms & Resources</h1><p>These entries show the current library catalog. Government forms link to the issuing agency’s current copy. Synthetic forms are general examples, not actual employer policy.</p><h3>Synthetic sample PDFs</h3><ul><li>Workplace Guide — synthetic sample, five pages</li><li>Company Directory — fictional contacts</li><li>Vacation Request — blank general request form</li><li>Workplace Concern / Complaint — blank general form</li><li>Weekly Timesheet — synthetic blank request resource</li><li>Sample Shift Patterns A–D — synthetic shift and change-request resource</li></ul><h3>Official government forms</h3><ul><li><a href="https://www.irs.gov/pub/irs-pdf/fw4.pdf">IRS 2026 Form W-4 — Employee’s Withholding Certificate</a></li><li><a href="https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf">U.S. Department of Labor FMLA WH-380-E — employee serious health condition certification</a></li><li><a href="https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-f.pdf">U.S. Department of Labor FMLA WH-380-F — family member serious health condition certification</a></li><li><a href="https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf">New York Paid Family Leave family-care packet — PFL-1, PFL-3, and PFL-4</a></li><li><a href="https://paidfamilyleave.ny.gov/forms">New York Paid Family Leave official forms page for other leave packages</a></li><li><a href="https://www.nyc.gov/site/idnyc/card/application-materials.page">NYC IDNYC application materials</a></li></ul><div class="note">If user-generated forms are added to the catalog, label the source “User-generated.” Do not treat user-added forms as official until reviewed.</div>'),
])

vacation = page('<div class="eyebrow">Synthetic blank form</div><h1>Vacation Request</h1><div class="banner">GENERAL SAMPLE ONLY — NOT AN APPROVAL OR ACTUAL EMPLOYER FORM</div><p>Submit through your employer’s approved process. A request is not approved until your supervisor or HR confirms it.</p><div class="grid"><div class="field">Employee name<div class="line"></div></div><div class="field">Employee ID (if required)<div class="line"></div></div><div class="field">Department / team<div class="line"></div></div><div class="field">Supervisor<div class="line"></div></div><div class="field">First day requested<div class="line"></div></div><div class="field">Last day requested<div class="line"></div></div></div><p>Request type: <span class="check"></span>Vacation <span class="check"></span>Personal time <span class="check"></span>Other: ____________________</p><div class="field">Notes (optional; do not include medical or sensitive personal details)<div class="box"></div></div><div class="grid"><div class="field">Employee signature<div class="line"></div></div><div class="field">Date submitted<div class="line"></div></div></div><h3>Supervisor / HR use</h3><p><span class="check"></span>Approved <span class="check"></span>Not approved <span class="check"></span>More information requested</p><div class="field">Response / notes<div class="box"></div></div><div class="grid"><div class="field">Reviewer name and title<div class="line"></div></div><div class="field">Date<div class="line"></div></div></div>')

complaint = page('<div class="eyebrow">Synthetic blank form</div><h1>Workplace Concern / Complaint</h1><div class="banner">GENERAL SAMPLE ONLY — USE YOUR EMPLOYER’S APPROVED HR OR REPORTING CHANNEL</div><p>This form is a fictional example for demonstrating a request for HR follow-up. It is not a legal filing, hotline, or confidential reporting service.</p><div class="note"><b>Privacy:</b> Include only information needed to describe the concern. Do not attach medical records, identity documents, or other sensitive records unless HR requests them through an approved protected channel.</div><div class="grid"><div class="field">Name (optional if permitted by process)<div class="line"></div></div><div class="field">Employee ID (only if requested)<div class="line"></div></div><div class="field">Preferred safe contact method<div class="line"></div></div><div class="field">Date submitted<div class="line"></div></div></div><p>Concern type: <span class="check"></span>Workplace conduct <span class="check"></span>Safety <span class="check"></span>Pay / timekeeping <span class="check"></span>Other</p><div class="field">What happened? Include dates, location, and relevant facts. Avoid unnecessary sensitive details.<div class="box large"></div></div><div class="field">What response or follow-up are you requesting?<div class="box"></div></div><p>Preferred follow-up: <span class="check"></span>Email <span class="check"></span>Phone <span class="check"></span>Meeting</p><div class="field">Signature (if required by employer process)<div class="line"></div></div>')

DOCS = {
    "synthetic-workplace-guide.pdf": html_doc("Synthetic Workplace Guide", policy),
    "synthetic-company-directory.pdf": html_doc("Synthetic Company Directory", directory),
    "synthetic-vacation-request.pdf": html_doc("Synthetic Vacation Request", vacation, compact=True),
    "synthetic-workplace-complaint.pdf": html_doc("Synthetic Workplace Complaint", complaint, compact=True),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not CHROME.is_file():
        raise SystemExit(f"Chrome not found: {CHROME}")
    selected = sys.argv[1:] or list(DOCS)
    unknown = set(selected) - set(DOCS)
    if unknown:
        raise SystemExit(f"Unknown resource names: {', '.join(sorted(unknown))}")
    with tempfile.TemporaryDirectory(prefix=".render-", dir=OUT) as tmp:
        tmp_path = Path(tmp)
        for filename in selected:
            markup = DOCS[filename]
            source = tmp_path / (filename.removesuffix(".pdf") + ".html")
            source.write_text(markup, encoding="utf-8")
            dest = OUT / filename
            subprocess.run([
                str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                "--disable-extensions", "--disable-background-networking", "--no-first-run",
                f"--user-data-dir={tmp_path / (filename.removesuffix('.pdf') + '-profile')}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={dest}", source.as_uri(),
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
            print(f"Created {dest}")


if __name__ == "__main__":
    main()
