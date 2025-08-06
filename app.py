from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import datetime

app = Flask(__name__)

# Define the path for the sign-off log file
SIGN_OFF_LOG_FILE = 'sign_off_log.txt'

# --- Data for the Playbook ---
roles_data = {
    "Audit Team Lead": {"personnel": "Ross Browne", "responsibilities": "Oversee audit process, maintain SOP, review annually or after each cycle"},
    "Audit Team Members": {"personnel": "Akira Devonish, Cherelle Griffith, etc.", "responsibilities": "Conduct audits per SOP, suggest improvements"},
    "Domain Lead": {"personnel": "Terry Bennett", "responsibilities": "Submit self-assessments, provide accurate info during interviews"},
    "Domain Co-Lead": {"personnel": "Destiny Holder", "responsibilities": "Assist Domain Lead in submitting self-assessments and providing information during interviews"},
    "Data Librarian": {"personnel": "Roger Barrow", "responsibilities": "Version control, secure storage of audit documentation"},
    "Domain Coordinator": {"personnel": "Dale Edwards", "responsibilities": "Oversight, SOP adherence checks, improvement recommendations"}
}

audit_lifecycle_data = [
    {"stage": "1. Audit Preparation", "timeline": "1–2 weeks before audit", "details": [
        "Select domain(s) to be audited.",
        "Share Preliminary Self-Assessment Form. (Includes: team structure, current activities, baseline compliance questions.)",
        "Set deadline for submission.",
        "Assign roles for interviews: Lead Interviewer, Scribe, Compliance Checker."
    ]},
    {"stage": "2. Question Development", "timeline": "1 week before interview", "details": [
        "Customize the Master Audit Template (V2) for the domain.",
        "Base questions on: Self-assessment responses, Known risks/gaps, Regulatory frameworks (GDPR, BDPA, EU AI Act, etc.)",
        "Include a mix of yes/no, short answer, and open-ended questions.",
        "Reference Template: Master_Audit_Template_V2.pdf"
    ]},
    {"stage": "3. Conducting Interviews", "timeline": "Scheduled per domain availability", "details": [
        "Set up interviews with domain leads.",
        "Use customized audit template as a guide.",
        "Remind participants about structure, confidentiality, and recording (if applicable).",
        "Stick to roles unless reassignment is needed due to team size."
    ]},
    {"stage": "4. Scoring & Evaluation", "timeline": "2–3 days post-interview", "details": [
        "Each team member scores their assigned sections. Use the provided rubric:",
        "Data Cleaning & Processing (Max: 40)",
        "Data Storage, Security & Privacy (Max: 30)",
        "Compliance & Accountability (Max: 20)",
        "Continuous Improvement & Culture (Max: 10)",
        "Compliance Score Summary: 90–100% (Compliant), 70–89% (Partially Compliant), < 70% (Non-Compliant)"
    ]},
    {"stage": "5. Compiling the Report", "timeline": "3–5 days post-scoring", "details": [
        "Include in final audit report: Domain overview, Interview summary, Scores per section, Risks, findings, and action recommendations.",
        "Example Report: Domain_C_ReportExample_2025_V1.pdf"
    ]},
    {"stage": "6. Submission & Feedback", "timeline": "1 week after reporting", "details": [
        "Submit reports to: Compliance Team Lead",
        "Relevant Domain Lead.",
        "Request feedback: Agree on remediation actions, Offer compliance support where needed."
    ]},
    {"stage": "7. Archiving & Continuous Improvement", "timeline": "Ongoing",
     "details": [
        "Archive all reports and notes securely (Data Librarian role).",
        "Conduct post-audit debrief: Lessons learned, SOP/process refinement, Feedback loop for the team.",
        "Example Form: DClean_Compliance_Q1-2025_VFinal.pdf"
    ]}
]

supporting_files_data = [
    {"title": "Master_Audit_Template_V2.pdf", "purpose": "Guide for customizing audit questions", "link": "Master_Audit_Template_V2.pdf"},
    {"title": "Domain_C_ReportExample_2025_V1.pdf", "purpose": "Sample final report", "link": "Domain_C_ReportExample_2025_V1.pdf"},
    {"title": "DClean_Compliance_Q1-2025_VFinal.pdf", "purpose": "Completed domain audit form", "link": "DClean_Compliance_Q1-2025_VFinal.pdf"},
    {"title": "Compliance_Audit_SOP (1).pdf", "purpose": "Standard Operating Procedure for Compliance Audits", "link": "Compliance_Audit_SOP (1).pdf"},
    {"title": "Self-Assessment Form", "purpose": "Baseline data gathering (Microsoft Form)", "link": "self_assessment_form_page"}
]

domains = [
    "Data Collection",
    "Data Cleaning",
    "Data Engineering",
    "Compliance, Ethics and Regulations"
]

domain_questions = {
    "Data Collection": [
        {"id": "q1_dc", "type": "radio", "question": "Is there a clear data collection policy in place?", "options": ["Yes", "No", "N/A"]},
        {"id": "q2_dc", "type": "textarea", "question": "Describe the primary methods used for data collection.", "placeholder": "e.g., APIs, manual input, web scraping..."},
        {"id": "q3_dc", "type": "radio", "question": "Are user consents obtained for all personal data collected?", "options": ["Yes", "No", "N/A"]},
        {"id": "q4_dc", "type": "text", "question": "What tools are used for data ingestion?", "placeholder": "e.g., Kafka, NiFi, custom scripts..."},
    ],
    "Data Cleaning": [
        {"id": "q1_dcl", "type": "radio", "question": "Are formal data validation rules applied during cleaning?", "options": ["Yes", "No", "N/A"]},
        {"id": "q2_dcl", "type": "textarea", "question": "Outline the process for handling missing or inconsistent data.", "placeholder": "e.g., imputation, deletion, flagging..."},
        {"id": "q3_dcl", "type": "radio", "question": "Is data quality regularly monitored and reported?", "options": ["Yes", "No", "N/A"]},
        {"id": "q4_dcl", "type": "text", "question": "Which data cleaning tools or scripts are utilized?", "placeholder": "e.g., Pandas, Spark, Trifacta..."},
    ],
    "Data Engineering": [
        {"id": "q1_de", "type": "radio", "question": "Are data pipelines documented and version-controlled?", "options": ["Yes", "No", "N/A"]},
        {"id": "q2_de", "type": "textarea", "question": "Describe the architecture of your data storage solutions.", "placeholder": "e.g., Data Lake, Data Warehouse, specific databases..."},
        {"id": "q3_de", "type": "radio", "question": "Are there automated tests for data pipeline integrity?", "options": ["Yes", "No", "N/A"]},
        {"id": "q4_de", "type": "text", "question": "What is the frequency of data backups?", "placeholder": "e.g., daily, weekly, continuously..."},
    ],
    "Compliance, Ethics and Regulations": [
        {"id": "q1_cer", "type": "radio", "question": "Does the team adhere to GDPR/BDPA regulations?", "options": ["Yes", "No", "N/A"]},
        {"id": "q2_cer", "type": "textarea", "question": "How are ethical considerations addressed in AI development?", "placeholder": "e.g., bias detection, fairness metrics..."},
        {"id": "q3_cer", "type": "radio", "question": "Are internal compliance audits conducted annually?", "options": ["Yes", "No", "N/A"]},
        {"id": "q4_cer", "type": "text", "question": "Which regulatory frameworks are most relevant to your current projects?", "placeholder": "e.g., EU AI Act, HIPAA..."},
    ]
}

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# NEW ROUTE
@app.route('/interactive_workflow')
def interactive_workflow():
    return render_template('interactive_workflow.html', lifecycle_stages=audit_lifecycle_data)

@app.route('/roles')
def roles():
    return render_template('roles.html', roles=roles_data)

@app.route('/lifecycle')
def lifecycle():
    return render_template('lifecycle.html', lifecycle_stages=audit_lifecycle_data)

@app.route('/audit_form', methods=['GET', 'POST'])
def audit_form():
    selected_domain = None
    questions_for_domain = []

    if request.method == 'POST':
        selected_domain = request.form.get('domain_select')
        if selected_domain and selected_domain in domain_questions:
            questions_for_domain = domain_questions[selected_domain]

    return render_template(
        'audit_form.html',
        domains=domains,
        selected_domain=selected_domain,
        questions=questions_for_domain
    )

@app.route('/submit_audit', methods=['POST'])
def submit_audit():
    submitted_domain = request.form.get('domain')
    audit_responses = {}

    if submitted_domain and submitted_domain in domain_questions:
        for q in domain_questions[submitted_domain]:
            response_key = q['id']
            audit_responses[q['question']] = request.form.get(response_key, 'No Response')

    return render_template('audit_summary.html',
                           submitted_domain=submitted_domain,
                           audit_responses=audit_responses)


@app.route('/score_calculator')
def score_calculator():
    return render_template('score_calculator.html')

@app.route('/calculate_score', methods=['POST'])
def calculate_score():
    data_cleaning = int(request.form.get('data_cleaning', 0))
    data_storage = int(request.form.get('data_storage', 0))
    compliance = int(request.form.get('compliance', 0))
    improvement = int(request.form.get('improvement', 0))

    total_score = data_cleaning + data_storage + compliance + improvement

    if 90 <= total_score <= 100:
        rating = "✅ Compliant"
        meaning = "This domain meets or exceeds the required compliance standards. No major risks were identified, though minor improvements should be considered to maintain a high level of performance."
    elif 70 <= total_score <= 89:
        rating = "⚠️ Partially Compliant"
        meaning = "This domain is generally compliant but has identified areas of risk and non-conformance. A formal remediation plan is required to address the gaps and prevent potential future non-compliance."
    else:
        rating = "❌ Non-Compliant"
        meaning = "This domain does not meet core compliance requirements. Immediate and urgent action is needed. A comprehensive corrective action plan must be developed and a re-audit is required to restore compliance."

    return jsonify(total_score=total_score, rating=rating, meaning=meaning)


@app.route('/supporting_files')
def supporting_files():
    return render_template('supporting_files.html', files=supporting_files_data)

@app.route('/self_assessment_form_page')
def self_assessment_form_page():
    return render_template('self_assessment_form.html')

@app.route('/sign_off', methods=['GET', 'POST'])
def sign_off():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        if user_name:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - {user_name} has reviewed the Playbook and SOP.\n"

            try:
                with open(SIGN_OFF_LOG_FILE, 'a') as f:
                    f.write(log_entry)
                message = "Thank you for signing off! Your entry has been recorded."
                return render_template('sign_off.html', message=message, show_form=False)
            except IOError:
                message = "Error: Could not write to the sign-off log file. Please try again later."
                return render_template('sign_off.html', message=message, show_form=True)
        else:
            message = "Please enter your name to sign off."
            return render_template('sign_off.html', message=message, show_form=True)

    return render_template('sign_off.html', message=None, show_form=True)


if __name__ == '__main__':
    app.run(debug=True)