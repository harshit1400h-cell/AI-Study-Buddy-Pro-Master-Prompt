import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_docs"
SAMPLE_DIR.mkdir(exist_ok=True)

def generate_pdf(filename: str, title: str, pages_data: list):
    pdf_path = SAMPLE_DIR / filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10
    )

    story = []

    for idx, page in enumerate(pages_data):
        if idx > 0:
            story.append(PageBreak())

        story.append(Paragraph(f"{title} — Page {idx + 1}", title_style))
        story.append(Spacer(1, 10))

        for section in page:
            if section.get("heading"):
                story.append(Paragraph(section["heading"], h2_style))
            if section.get("body"):
                story.append(Paragraph(section["body"], body_style))

    doc.build(story)
    print(f"Generated real PDF: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    p1 = [
        [
            {"heading": "1. Artificial Neural Networks and Perceptrons", "body": "An Artificial Neural Network (ANN) is defined as a computational model inspired by the biological nervous system, designed to recognize complex patterns across high-dimensional data. The fundamental processing unit is the Perceptron or Artificial Neuron, which calculates the weighted sum of inputs and passes this scalar through an activation function."},
            {"heading": "2. Activation Functions and Non-Linearity", "body": "Without non-linear activation functions, any deep multi-layer neural network collapses into a simple linear regression regardless of depth. ReLU (Rectified Linear Unit) is defined as f(x) = max(0, x), preventing gradient vanishing for positive activations. Sigmoid scales inputs between 0 and 1, frequently used in binary output layers. Softmax normalizes logit vectors into probability distributions summing to 1.0."}
        ],
        [
            {"heading": "3. Gradient Descent Optimization", "body": "Gradient Descent is defined as an iterative optimization algorithm used to minimize the objective loss function by updating parameter weights in the opposite direction of the gradient vector. The weight update rule is w_new = w_old - alpha * grad(L), where alpha denotes the learning rate parameter."},
            {"heading": "4. Backpropagation Calculus & Regularization", "body": "Backpropagation refers to the systematic application of the calculus Chain Rule to compute partial derivatives of the loss function with respect to every weight throughout all network layers. Overfitting occurs when a neural network memorizes training set noise rather than generalizing underlying structural features. Dropout randomly deactivates a fraction of neurons during training."}
        ]
    ]

    generate_pdf("Deep_Learning_and_Neural_Networks_Foundations.pdf", "Deep Learning Foundations", p1)

    p2 = [
        [
            {"heading": "1. Human Memory Systems (Atkinson-Shiffrin Model)", "body": "Human memory is organized into three distinct operational stores: Sensory Memory (holds raw visual and auditory impressions for fractions of a second), Working Memory (holds 4 to 7 informational chunks for 15 to 30 seconds), and Long-Term Memory (virtually limitless repository for consolidated knowledge)."},
            {"heading": "2. The Ebbinghaus Forgetting Curve", "body": "Hermann Ebbinghaus discovered that newly acquired theoretical information degrades exponentially over time without deliberate review. Up to 70% of unreviewed material is lost within the initial 24 to 48 hours following exposure."}
        ],
        [
            {"heading": "3. Active Recall & Evidence-Based Pedagogy", "body": "Active Recall refers to the pedagogical practice of deliberately stimulating memory retrieval without looking at original study notes. Effortful retrieval testing dramatically enhances neural synaptic consolidation."},
            {"heading": "4. Spaced Repetition and the Leitner System", "body": "The Spaced Repetition technique schedules review sessions at expanding time intervals. The Leitner Box System organizes flashcards into progressive tiers from Box 1 (daily) to Box 5 (mastered monthly). Incorrect answers reset the card to Box 1."}
        ]
    ]

    generate_pdf("Cognitive_Psychology_and_Learning_Science.pdf", "Cognitive Psychology & Learning Science", p2)

