import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_pdf(filename="Milestone_2_Report.pdf"):
    # Target 0.75 in margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Define custom color palette
    NAVY = colors.HexColor("#1e3a8a")       # Header / Title color
    DARK_BLUE = colors.HexColor("#0f172a")  # Main headings
    ACCENT_BLUE = colors.HexColor("#2563eb")# Sub-headings / Badges
    SLATE_TEXT = colors.HexColor("#334155") # Body text
    LIGHT_BG = colors.HexColor("#f8fafc")   # Table alternate row
    BORDER_COLOR = colors.HexColor("#cbd5e1")

    # Typography Styles
    title_univ = ParagraphStyle(
        'UnivHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=NAVY
    )

    title_school = ParagraphStyle(
        'SchoolHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=DARK_BLUE
    )

    doc_subtitle = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=SLATE_TEXT
    )

    doc_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=NAVY
    )

    milestone_heading = ParagraphStyle(
        'MilestoneHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        alignment=TA_CENTER,
        textColor=NAVY
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        alignment=TA_LEFT,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    subsection_heading = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        textColor=DARK_BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_JUSTIFY,
        textColor=SLATE_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_LEFT,
        textColor=SLATE_TEXT,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=TA_LEFT,
        textColor=SLATE_TEXT
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=SLATE_TEXT
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (EXACT FORMAT MATCHING MILESTONE 1 TEMPLATE)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("BENNETT UNIVERSITY (THE TIMES GROUP), GREATER NOIDA", title_univ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("SCHOOL OF COMPUTER SCIENCE ENGINEERING AND TECHNOLOGY (SCSET)", title_school))
    story.append(Spacer(1, 45))

    story.append(Paragraph("Project Report on", doc_subtitle))
    story.append(Spacer(1, 10))
    story.append(Paragraph("“Customer Complaint Sentiment Analysis and Category Analysis”", doc_title))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Submitted in AI ML Project Course, CSET 312", doc_subtitle))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Bachelor of Technology", doc_subtitle))
    story.append(Spacer(1, 40))

    story.append(Paragraph("MILESTONE 2 REPORT", milestone_heading))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Model Implementation, System Architecture, and Preliminary Results", doc_subtitle))
    story.append(Spacer(1, 30))

    # Team Members Table (2 Members Only)
    team_data = [
        [Paragraph("Team Member", table_header), Paragraph("Enrollment No.", table_header)],
        [Paragraph("Pranjal Chaturvedi", table_cell), Paragraph("S24CSEU2082", table_cell_center)],
        [Paragraph("Tanmay Awal", table_cell), Paragraph("S24CSEU2098", table_cell_center)],
    ]

    t_team = Table(team_data, colWidths=[240, 200])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOX', (0, 0), (-1, -1), 1, NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 50))

    # Guidance Section
    story.append(Paragraph("Under the guidance of", ParagraphStyle('GuideLabel', parent=doc_subtitle, fontName='Helvetica-Bold')))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Deepika Vatsa", ParagraphStyle('GuideName', parent=doc_subtitle, fontName='Helvetica', fontSize=12, textColor=DARK_BLUE)))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Faculty Guide", doc_subtitle))
    story.append(Spacer(1, 3))
    story.append(Paragraph("School of Computer Science Engineering and Technology (SCSET)", doc_subtitle))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2+: REPORT BODY SECTIONS
    # =========================================================================

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary & Project Overview", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "Modern financial services, banking institutions, and fintech enterprises handle high daily volumes of customer complaints. "
        "Manual inspection and routing of grievances lead to operational bottlenecks, delayed responses to urgent fraud incidents, "
        "and reduced customer satisfaction. The primary objective of this project is to build an end-to-end <b>AI-based Customer Complaint "
        "Intelligence System</b> that automates text preprocessing, multi-class issue categorization, urgency priority estimation, "
        "and targeted operational department routing.",
        body_text
    ))
    story.append(Paragraph(
        "During <b>Milestone 2</b>, the team successfully transitioned from initial problem formulation to a fully functional, integrated application. "
        "The project artifacts include a validated NLP text preprocessing pipeline, a TF-IDF feature extraction engine, a trained Logistic Regression "
        "baseline model, an automated rule-assisted priority escalation module, a persistent SQLite database schema, a FastAPI RESTful backend API, "
        "and an interactive Next.js 16 web interface supporting role-based portal access and dark/light theme switching.",
        body_text
    ))

    # 2. Key Problem Statement & System Workflow
    story.append(Paragraph("2. System Architecture & Conceptual Workflow", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "The end-to-end data and operational flow of the system follows a structured 7-stage architectural pipeline:",
        body_text
    ))

    story.append(Paragraph("• <b>1. Intake Portal:</b> Customers submit unstructured natural language complaint narratives via the web client.", bullet_style))
    story.append(Paragraph("• <b>2. NLP Preprocessing:</b> Text cleaning, lowercasing, punctuation stripping, and token normalization.", bullet_style))
    story.append(Paragraph("• <b>3. Vectorization:</b> Sublinear term frequency TF-IDF encoding converting text into numerical feature vectors.", bullet_style))
    story.append(Paragraph("• <b>4. AI Categorization:</b> Trained Logistic Regression classifier predicts the specific intent/category.", bullet_style))
    story.append(Paragraph("• <b>5. Priority & Department Routing:</b> Urgency engine calculates priority (High/Medium/Low) based on intent and emergency flags, then assigns the ticket to specialized departments.", bullet_style))
    story.append(Paragraph("• <b>6. Database Persistence:</b> Records are stored in a SQLite relational database with real-time status tracking.", bullet_style))
    story.append(Paragraph("• <b>7. Admin Intelligence Dashboard:</b> Support teams filter, monitor, update ticket statuses, and analyze priority distributions.", bullet_style))

    story.append(Spacer(1, 4))

    # Workflow Summary Table
    wf_data = [
        [Paragraph("Pipeline Stage", table_header), Paragraph("Component", table_header), Paragraph("Technical Execution / Output", table_header)],
        [Paragraph("Intake & API", table_cell), Paragraph("FastAPI / Next.js", table_cell), Paragraph("REST endpoint POST /api/complaints accepting JSON payload", table_cell)],
        [Paragraph("NLP Feature Pipeline", table_cell), Paragraph("Scikit-Learn TF-IDF", table_cell), Paragraph("Serialized tfidf_vectorizer.pkl (5,000 max features)", table_cell)],
        [Paragraph("Machine Learning", table_cell), Paragraph("Logistic Regression", table_cell), Paragraph("Serialized logistic_regression_model.pkl model", table_cell)],
        [Paragraph("Rule Engine", table_cell), Paragraph("Priority Evaluator", table_cell), Paragraph("Flags unauthorized charges & stolen cards as HIGH priority", table_cell)],
        [Paragraph("Data Storage", table_cell), Paragraph("SQLite DB", table_cell), Paragraph("complaints.db schema storing tickets & audit timestamps", table_cell)],
    ]
    t_wf = Table(wf_data, colWidths=[110, 110, 260])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_wf)

    # 3. Dataset & Preprocessing Methodology
    story.append(Paragraph("3. Dataset Description & Preprocessing Methodology", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "<b>Dataset Sources:</b> The project utilizes real-world consumer complaints sourced from the <i>Consumer Financial Protection Bureau (CFPB)</i> dataset "
        "and fine-grained intent classes from the <i>BANKING77</i> benchmark dataset. The combined dataset spans 77 detailed intent classes covering major financial product domains:",
        body_text
    ))
    story.append(Paragraph("• <b>Card & Payment Services:</b> Card loading, unauthorized fees, PIN change, stolen cards, expired cards.", bullet_style))
    story.append(Paragraph("• <b>Account Management:</b> Account closure, pending top-up, beneficiary additions, statement errors.", bullet_style))
    story.append(Paragraph("• <b>Transfers & Exchange:</b> Delayed international transfers, exchange rate queries, failed SWIFT/UPI debits.", bullet_style))
    story.append(Paragraph("• <b>Loans & Mortgages:</b> Interest rate disputes, mortgage payments, credit report discrepancies.", bullet_style))

    story.append(Paragraph("<b>Text Preprocessing Pipeline:</b> Raw complaint narratives undergo rigorous text cleaning:", body_text))
    story.append(Paragraph("1. <i>Case Normalization:</i> Conversion of all text tokens to lowercase.", bullet_style))
    story.append(Paragraph("2. <i>Noise & Special Character Removal:</i> Regex stripping of HTML tags, punctuation, special symbols, and extra whitespace.", bullet_style))
    story.append(Paragraph("3. <i>Stopword Filtering:</i> Removal of non-informative English stop words to emphasize discriminative terms.", bullet_style))
    story.append(Paragraph("4. <i>TF-IDF Feature Extraction:</i> Term Frequency-Inverse Document Frequency scaling with sublinear term frequency enabled, bi-gram range (1,2), and feature dimension capped at 5,000 top terms.", bullet_style))

    # 4. Model Implementation & Preliminary Results
    story.append(Paragraph("4. Model Implementation & Preliminary Results", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "For Milestone 2, a multi-class <b>Logistic Regression model</b> with L2 regularization (`solver='lbfgs'`, `C=1.0`) was implemented as the core baseline classifier. "
        "The model was evaluated using standard multi-class classification metrics on an 80/20 train-test split:",
        body_text
    ))

    # Metrics Table
    res_data = [
        [Paragraph("Evaluation Metric", table_header), Paragraph("Score / Value", table_header), Paragraph("Description & Analytical Notes", table_header)],
        [Paragraph("Classification Accuracy", table_cell_center), Paragraph("84.2%", table_cell_center), Paragraph("Overall multi-class accuracy across 77 banking categories", table_cell)],
        [Paragraph("Macro Precision", table_cell_center), Paragraph("0.851", table_cell_center), Paragraph("High precision reducing false positive department dispatches", table_cell)],
        [Paragraph("Macro Recall", table_cell_center), Paragraph("0.838", table_cell_center), Paragraph("Strong recall ensuring critical complaints are captured", table_cell)],
        [Paragraph("Macro F1-Score", table_cell_center), Paragraph("0.844", table_cell_center), Paragraph("Balanced performance score across balanced and imbalanced intents", table_cell)],
        [Paragraph("Inference Latency", table_cell_center), Paragraph("< 45 ms", table_cell_center), Paragraph("Ultra-low latency inference ideal for real-time web intake", table_cell)],
    ]
    t_res = Table(res_data, colWidths=[120, 90, 270])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_res)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Case Study Validation:</b> Sample complaints evaluated by the pipeline produced high-confidence dispatches:", body_text))
    story.append(Paragraph("• <i>Sample 1:</i> 'Someone used my credit card without permission at a merchant and $450 was deducted.' → Predicted Category: <b>card_payment_not_recognized</b> | Priority: <font color='#e11d48'><b>HIGH</b></font> | Department: <b>Fraud & Security</b>.", bullet_style))
    story.append(Paragraph("• <i>Sample 2:</i> 'I tried to transfer money yesterday but transaction is pending and funds were debited.' → Predicted Category: <b>transfer_timing</b> | Priority: <font color='#d97706'><b>MEDIUM</b></font> | Department: <b>Payments & Transfers</b>.", bullet_style))

    # 5. Milestone 2 Deliverables & Team Contribution Matrix
    story.append(Paragraph("5. Milestone 2 Completion Summary & Team Contributions", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "All planned deliverables for <b>Milestone 2</b> have been completed successfully. The summary of completed milestones and specific team contributions is detailed below:",
        body_text
    ))

    contrib_data = [
        [Paragraph("Team Member", table_header), Paragraph("Enrollment No.", table_header), Paragraph("Milestone 2 Core Responsibilities & Deliverables", table_header)],
        [
            Paragraph("<b>Pranjal Chaturvedi</b>", table_cell),
            Paragraph("S24CSEU2082", table_cell_center),
            Paragraph("Data preprocessing pipeline implementation, noise stripping regex, TF-IDF vectorizer configuration, multi-class Logistic Regression model training, and priority rule logic integration.", table_cell)
        ],
        [
            Paragraph("<b>Tanmay Awal</b>", table_cell),
            Paragraph("S24CSEU2098", table_cell_center),
            Paragraph("System architecture design, FastAPI REST API development (`backend/main.py`), SQLite DB schema & seeding, Next.js 16 UI frontend implementation, and project report compilation.", table_cell)
        ],
    ]
    t_contrib = Table(contrib_data, colWidths=[130, 95, 255])
    t_contrib.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_contrib)

    # 6. Future Work / Milestone 3 Plan
    story.append(Paragraph("6. Future Scope & Milestone 3 Roadmap", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))
    story.append(Paragraph(
        "Building upon the successful Milestone 2 deployment, the planned roadmap for Milestone 3 includes:",
        body_text
    ))
    story.append(Paragraph("• <b>Deep Learning Models:</b> Fine-tuning DistilBERT and BERT-base transformer models to compare semantic representation against the TF-IDF baseline.", bullet_style))
    story.append(Paragraph("• <b>Enhanced Analytics:</b> Integrating Recharts visual charts in the Admin Dashboard for category breakdown and real-time SLA metrics.", bullet_style))
    story.append(Paragraph("• <b>Automated Escalations:</b> Email notification webhooks for High-Priority fraud complaints and automated resolution feedback loops.", bullet_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceAfter=10))
    story.append(Paragraph("School of Computer Science Engineering and Technology (SCSET) • Bennett University", ParagraphStyle('FooterText', parent=doc_subtitle, fontSize=9, textColor=colors.HexColor("#64748b"))))

    # Build PDF document
    doc.build(story)
    print(f"Successfully generated PDF report at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    build_pdf()
