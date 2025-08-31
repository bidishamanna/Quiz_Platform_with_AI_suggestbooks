# payment/utils.py
from io import BytesIO
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def send_invoice_pdf(user, books, total, transaction_id, timestamp):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Invoice")

    # User Details
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Customer: {user.username} ({user.email})")
    p.drawString(50, height - 120, f"Transaction ID: {transaction_id}")
    p.drawString(50, height - 140, f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    # Books
    y = height - 180
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Purchased Books:")
    y -= 20
    p.setFont("Helvetica", 12)
    for book in books:
        p.drawString(70, y, f"- {book.title}")
        y -= 20

    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y - 20, f"Total Amount: ₹{total}")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    # Send Email
    email = EmailMessage(
        subject="Your Invoice - BuyBook",
        body="Thank you for your purchase. Please find attached your invoice.",
        from_email="no-reply@buybook.com",
        to=[user.email],
    )
    email.attach(f"invoice_{transaction_id}.pdf", pdf, "application/pdf")
    email.send()
