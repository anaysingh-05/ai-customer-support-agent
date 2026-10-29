import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("pdfs", exist_ok=True)

documents = {
    "billing_policy.pdf": """
BILLING AND REFUND POLICY

1. Customers who notice duplicate charges should contact customer support.
2. Customers should provide transaction dates, amounts, and order references.
3. The billing team must investigate duplicate charge complaints.
4. Refunds are subject to investigation and company approval.
""",
    "technical_support_policy.pdf": """
TECHNICAL SUPPORT POLICY

1. Customers should describe the technical problem they are experiencing.
2. Customers may provide error messages and steps to reproduce the issue.
3. Technical support will investigate reported technical problems.
4. Complex issues may be escalated to the technical team.
""",
    "account_policy.pdf": """
CUSTOMER ACCOUNT POLICY

1. Account access issues must be verified by the support team.
2. Customers should never share their passwords.
3. Suspicious account activity should be reported to customer support.
4. Account recovery requests are subject to identity verification.
"""
}

for filename, content in documents.items():
    path = os.path.join("pdfs", filename)
    pdf = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 60

    for line in content.strip().splitlines():
        line = line.strip()

        if not line:
            y -= 12
            continue

        if y < 60:
            pdf.showPage()
            y = height - 60

        pdf.drawString(50, y, line[:100])
        y -= 20

    pdf.save()
print("Three sample policy PDFs created successfully in the pdfs folder.")