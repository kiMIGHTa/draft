from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(result, output_path, include_timestamps=True):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Transcript", styles["Title"]))
    story.append(Spacer(1, 12))

    for seg in result["segments"]:
        text = seg["text"].strip()

        if include_timestamps:
            start = seg["start"]
            line = f"[{start:.2f}] {text}"
        else:
            line = text

        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
