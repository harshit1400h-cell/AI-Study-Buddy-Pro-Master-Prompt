import uuid
from datetime import datetime
from typing import List, Dict, Any

SAMPLE_TOPICS = [
    {
        "id": "sample-ai-deep-learning",
        "filename": "Deep_Learning_and_Neural_Networks_Foundations.pdf",
        "file_type": "sample",
        "file_size": 24800,
        "page_count": 3,
        "summary": "Comprehensive overview of artificial neural networks, activation functions, backpropagation calculus, and transformer self-attention mechanisms.",
        "pages": [
            {
                "page_number": 1,
                "text": """Deep Learning and Artificial Neural Networks: Foundations and Architecture

1. Introduction to Artificial Neurons
An Artificial Neural Network (ANN) is defined as a computational model inspired by the biological nervous system, designed to recognize complex patterns across high-dimensional data. The fundamental processing unit is the Perceptron or Artificial Neuron, which calculates the weighted sum of inputs and passes this scalar through an activation function.

Mathematically, given inputs x_1, x_2, ..., x_n with corresponding synaptic weights w_1, w_2, ..., w_n and bias b:
z = sum(w_i * x_i) + b
y = f(z), where f is the activation function.

2. Activation Functions and Non-Linearity
Without non-linear activation functions, any deep multi-layer neural network collapses into a simple linear regression regardless of depth.
- ReLU (Rectified Linear Unit): Defined as f(x) = max(0, x). ReLU is the standard activation function in modern deep networks due to its computational simplicity and prevention of gradient vanishing for positive activations.
- Sigmoid Function: Defined as sigma(x) = 1 / (1 + e^(-x)). Scales inputs into an open interval between 0 and 1, frequently used in binary output classification layers.
- Softmax Function: Normalizes an unconstrained logit vector into a probability distribution summing to exactly 1.0, standard for multi-class classification."""
            },
            {
                "page_number": 2,
                "text": """Gradient Descent and Backpropagation Calculus

3. The Optimization Mechanism: Gradient Descent
Gradient Descent is defined as an iterative optimization algorithm used to minimize the objective loss function by updating parameter weights in the opposite direction of the gradient vector.
The weight update rule is:
w_new = w_old - alpha * grad(L)
where alpha denotes the learning rate parameter. If alpha is too small, convergence is prohibitively slow; if alpha is too large, the optimizer oscillates and diverges away from local minima.

4. Backpropagation Algorithm
Backpropagation refers to the systematic application of the calculus Chain Rule to compute partial derivatives of the scalar loss function with respect to every weight throughout all network layers.
The forward pass propagates inputs through hidden layers to produce predictions and compute loss. The backward pass propagates error gradients backwards from the output layer to update weights.

5. Regularization and Preventing Overfitting
Overfitting occurs when a neural network memorizes training set noise rather than generalizing underlying structural features, resulting in low training loss but high validation error.
- Dropout: Randomly deactivates a fraction p (e.g., 0.2 to 0.5) of hidden neuron activations during forward passes, preventing co-adaptation of weights.
- Weight Decay (L2 Regularization): Adds a penalty proportional to the squared magnitude of weights to the objective loss function."""
            },
            {
                "page_number": 3,
                "text": """Transformer Architectures and Self-Attention

6. The Transformer Revolution
The Transformer architecture is a deep learning paradigm relying exclusively on the Self-Attention mechanism, eliminating sequential recurrent loops (RNNs) and allowing parallel training over vast text corpora.

7. Scaled Dot-Product Attention
Attention is mathematically defined as:
Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V
where:
- Q (Query): Represents what the token is seeking.
- K (Key): Represents what features the other tokens offer.
- V (Value): The actual contextual information contained in each token.
- sqrt(d_k): Scaling factor to prevent large dot-product magnitudes from pushing softmax into saturating regions with vanishing gradients.

Multi-Head Attention projects queries, keys, and values into multiple representation subspaces, enabling the model to jointly attend to information from different representation positions simultaneously."""
            }
        ]
    },
    {
        "id": "sample-cognitive-psychology",
        "filename": "Cognitive_Psychology_and_Learning_Science.pdf",
        "file_type": "sample",
        "file_size": 19500,
        "page_count": 2,
        "summary": "Scientific principles of memory consolidation, the Ebbinghaus forgetting curve, spaced repetition algorithms, and active recall mastery.",
        "pages": [
            {
                "page_number": 1,
                "text": """Cognitive Psychology: Human Memory and Learning Mechanics

1. Multi-Store Model of Memory (Atkinson-Shiffrin)
Human memory is organized into three distinct operational stores:
- Sensory Memory: Holds raw sensory impressions (iconic visual, echoic auditory) for fractions of a second.
- Working Memory (Short-Term Memory): A finite cognitive workspace capable of actively maintaining approximately 4 to 7 informational chunks for 15 to 30 seconds without active rehearsal.
- Long-Term Memory: A virtually limitless repository where consolidated knowledge, procedural skills, and episodic experiences are stored indefinitely.

2. The Ebbinghaus Forgetting Curve
Hermann Ebbinghaus discovered that newly acquired theoretical information degrades exponentially over time if no deliberate review occurs. Up to 70% of unreviewed material is lost within the initial 24 to 48 hours following exposure.
However, each strategic repetition resets the forgetting trajectory and flattens the decay curve, prolonging long-term retention."""
            },
            {
                "page_number": 2,
                "text": """High-Yield Learning Strategies: Evidence-Based Pedagogy

3. Active Recall vs. Passive Review
Active Recall refers to the pedagogical practice of deliberately stimulating memory retrieval without looking at original study notes.
Cognitive studies show that passive review (such as re-reading textbooks or highlighting text) creates an illusion of competence, whereas effortful retrieval testing dramatically enhances neural synaptic plasticity and consolidation.

4. Spaced Repetition and the Leitner System
The Spaced Repetition technique schedules review sessions at expanding time intervals (e.g., Day 1, Day 3, Day 7, Day 16, Day 35).
The Leitner Box System organizes flashcards into progressive tiers:
- Box 1: Unfamiliar cards reviewed daily.
- Box 2: Moderately familiar cards reviewed every 3 days.
- Box 3: Confident cards reviewed weekly.
- Box 4 and 5: Mastered concepts reviewed monthly.
When a student answers incorrectly, the card immediately resets to Box 1, guaranteeing that weak areas receive maximized cognitive focus."""
            }
        ]
    }
]

