# BioGen: AI-Powered Disease Prediction & Nutrition Guide

**BioGen** is an advanced health assistant that leverages machine learning to predict over 24 different diseases from user-described symptoms. It provides immediate, condition-specific nutritional recovery plans and features an integrated medical chatbot powered by MedGemma-4B-IT for a comprehensive digital health experience.

### 📸 Application Preview

| Home & Diagnosis | About & Diseases | How It Works |
| :---: | :---: | :---: |
| ![Home](home_preview.png) | ![About](about_preview.png) | ![How It Works](workflow_preview.png) |

## 🚀 Live Demo

Check out the live application here: [BioGen on AWS Elastic Beanstalk](http://diseaseprediction-env.eba-3qpujgpa.ap-south-1.elasticbeanstalk.com/)

## 🎯 Project Highlights

- **Predictive AI**: A local Scikit-Learn (SVM) model trained to recognize 24 conditions with high precision.
- **Holistic Recovery**: Beyond diagnosis, the app provides actionable "Essential Nutrition" steps.
- **Medical LLM**: Integrated with Google's MedGemma via Hugging Face for nuanced health conversations.
- **Premium UX**: Modern glassmorphic design with real-time feedback and smooth transitions.

## 🏥 Supported Diseases (24)

BioGen is currently trained to analyze and provide guidance for the following conditions:
- **Skin**: Acne, Fungal Infection, Psoriasis, Impetigo, Chicken Pox
- **Chronic**: Diabetes, Hypertension, Arthritis, Migraine, Cervical Spondylosis, Varicose Veins
- **Infections**: Dengue, Malaria, Typhoid, Common Cold, UTI
- **Digestive**: GERD, Peptic Ulcer Disease, Hemorrhoids, Jaundice
- **Respiratory**: Bronchial Asthma, Pneumonia
- **Reactions**: Allergy, Drug Reaction

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **ML**: Scikit-Learn, Joblib, TF-IDF Vectorization
- **Frontend**: ES6 JavaScript, Vanilla CSS3 (Glassmorphism)
- **AI Support**: Hugging Face Inference API

## 📦 Installation & Quick Start

1. **Clone & Enter**:
   ```bash
   git clone <repository-url>
   cd "disease prediction"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API**:
   Add your `HF_API_TOKEN` to a `.env` file in the root directory.

4. **Launch**:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000`

## ⚠️ Experimental & Unstable Areas

- **Unknown Condition Detection**: The "Confidence Margin" logic is experimental. If symptoms are ambiguous, the AI may categorize them as "Unknown" to prioritize safety.
- **LLM Latency**: The chatbot depends on Hugging Face's inference servers; response times may vary based on model loading state.
- **Model Thresholds**: Confidence thresholds (currently 40%) are tunable in `app.py` for varying levels of diagnostic strictness.

## ⚖️ Medical Disclaimer
**BioGen is an AI prototype for educational purposes.** The results provided are not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for any medical concerns.
