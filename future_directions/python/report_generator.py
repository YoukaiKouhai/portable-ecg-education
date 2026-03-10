from reportlab.pdfgen import canvas

def generate_report(filename, hr, rhythm):

    c = canvas.Canvas(filename)

    c.setFont("Helvetica",14)

    c.drawString(100,750,"Portable ECG Report")

    c.drawString(100,700,f"Heart Rate: {hr} BPM")

    c.drawString(100,670,f"Rhythm: {rhythm}")

    c.save()