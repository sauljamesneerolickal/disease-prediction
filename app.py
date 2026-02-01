from flask import Flask, render_template, request, jsonify
import requests
import os
import joblib
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- Local Model Loading ---
MODEL_PATH = "c:/disease prediction/model/"
try:
    svm_model = joblib.load(os.path.join(MODEL_PATH, "svm_model.pkl"))
    tfidf_vectorizer = joblib.load(os.path.join(MODEL_PATH, "tfidf_vectorizer.pkl"))
    label_encoder = joblib.load(os.path.join(MODEL_PATH, "label_encoder.pkl"))
    print("Local model files loaded successfully.")
except Exception as e:
    print(f"Error loading model files: {e}")
    svm_model = tfidf_vectorizer = label_encoder = None

# Hugging Face Configuration (Keeping for Chatbot feature specifically)
HF_API_URL = "https://api-inference.huggingface.co/models/google/medgemma-4b-it"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

@app.route('/')
def home():
    return render_template('index.html', active_page='home')

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html', active_page='how_it_works')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')

@app.route('/predict', methods=['POST'])
def predict():
    if not svm_model or not tfidf_vectorizer:
        return jsonify({'error': 'Model not loaded on server.'}), 500
        
    data = request.json
    symptoms = data.get('symptoms', '')
    
    if not symptoms:
        return jsonify({'error': 'No symptoms provided.'}), 400

    try:
        # 1. Clean/Preprocess (matching training format - simplified here)
        clean_text = symptoms.lower().strip()
        
        # 2. Vectorize
        features = tfidf_vectorizer.transform([clean_text])
        
        # 3. Decision Function Scores
        import numpy as np
        features_dense = features.toarray()
        
        # Check if any features were identified at all
        if np.count_nonzero(features_dense) == 0:
            return jsonify({
                'disease': "Unknown Condition",
                'confidence': "0%",
                'original_input': symptoms
            })

        # Get raw decision scores
        scores = svm_model.decision_function(features_dense)[0]

        # 1. Softmax for Confidence Percentage
        exp_scores = np.exp(scores - np.max(scores))   # numerical stability
        probabilities = exp_scores / np.sum(exp_scores)
        best_index = np.argmax(probabilities)
        confidence_val = probabilities[best_index]
        confidence_pct = f"{round(confidence_val * 100, 1)}%"

        # 2. Confidence Margin (Unknown Detection)
        sorted_scores = np.sort(scores)[::-1]
        margin = sorted_scores[0] - sorted_scores[1]

        # Thresholds (tunable)
        PERCENT_THRESHOLD = 0.40     # 40%
        MARGIN_THRESHOLD = 0.5       # score gap

        # FINAL DECISION
        if confidence_val < PERCENT_THRESHOLD or margin < MARGIN_THRESHOLD:
            disease = "Unknown Condition"
        else:
            disease = label_encoder.inverse_transform([best_index])[0]

        # --- Dynamic Recovery & Diet Logic ---
        RECOVERY_PLANS = {
            "Acne": {
                "title": "Clear Skin Detox",
                "tags": ["Low Glycemic", "Anti-inflammatory"],
                "details": [
                    "High-zinc foods like pumpkin seeds and lentils",
                    "Rich in Omega-3 (Walnuts, Chia seeds)",
                    "Increase probiotic intake (Yogurt, Kefir)",
                    "Limit dairy and high-sugar processed foods"
                ]
            },
            "Fungal Infection": {
                "title": "Anti-Fungal Support",
                "tags": ["Low Sugar", "Probiotic Rich"],
                "details": [
                    "Garlic and onions for natural antifungal properties",
                    "Unsweetened yogurt for healthy gut flora",
                    "Coconut oil (contains caprylic acid)",
                    "Avoid yeasty breads and sugary snacks"
                ]
            },
            "Psoriasis": {
                "title": "Autoimmune Guard",
                "tags": ["Anti-inflammatory", "Mediterranean"],
                "details": [
                    "Fatty fish (Salmon) for Omega-3",
                    "Leafy greens and colorful berries",
                    "Turmeric and ginger in daily meals",
                    "Avoid nightshade vegetables (Potatoes, Tomatoes) if sensitive"
                ]
            },
            "Diabetes": {
                "title": "Glucose Balance",
                "tags": ["Low GI", "High Fiber"],
                "details": [
                    "Complex carbs like Brown rice and Quinoa",
                    "Fiber-rich legumes and beans",
                    "Healthy fats from Avocados and Nuts",
                    "Strictly monitor portions of sugary fruits"
                ]
            },
            "Hypertension": {
                "title": "DASH-Inspired Plan",
                "tags": ["Low Sodium", "Heart Healthy"],
                "details": [
                    "Potassium-rich foods (Bananas, Spinach)",
                    "Magnesium sources like almonds and dark leaf greens",
                    "Whole grains and lean protein",
                    "Limit salt intake and processed meats"
                ]
            },
            "Malaria": {
                "title": "High-Energy Recovery",
                "tags": ["Energy Boost", "Iron Rich"],
                "details": [
                    "Iron-rich foods (Spinach, Pomegranate)",
                    "High-vitamin C fruits to aid iron absorption",
                    "Electrolyte-rich fluids (Coconut water)",
                    "Easy-to-digest protein like boiled eggs"
                ]
            },
            "Dengue": {
                "title": "Platelet Support",
                "tags": ["Hydrating", "Easy Digest"],
                "details": [
                    "Papaya leaf extract or fresh papaya",
                    "Plenty of fluids (Water, Juices, Soups)",
                    "Vitamin K rich foods (Broccoli, Kale)",
                    "Soft diet: Porridge, mashed vegetables"
                ]
            },
            "Typhoid": {
                "title": "Gentle Digestion",
                "tags": ["Low Fiber", "High Calorie"],
                "details": [
                    "High-calorie meals like bananas and boiled potatoes",
                    "Well-cooked rice and light vegetable broths",
                    "Maintain strict hydration with boiled water",
                    "Avoid raw vegetables and tough fiber"
                ]
            },
            "GERD": {
                "title": "Acid Soothe",
                "tags": ["Low Acid", "Digestive"],
                "details": [
                    "Alkaline foods (Melons, Bananas, Oatmeal)",
                    "Non-citrus fruits and ginger tea",
                    "Lean meats (Chicken, Fish) - grilled or baked",
                    "Avoid spicy, oily, and caffeinated drinks"
                ]
            },
            "Bronchial Asthma": {
                "title": "Respiratory Support",
                "tags": ["Anti-inflammatory", "Magnesium Support"],
                "details": [
                    "Magnesium-rich dark chocolate and nuts",
                    "Vitamin D sources like eggs and mushrooms",
                    "Apples for lung function improvement",
                    "Avoid sulfites found in dried fruits"
                ]
            },
            "Jaundice": {
                "title": "Liver Detox Plan",
                "tags": ["Low Fat", "Hydrating"],
                "details": [
                    "Plenty of water and fresh fruit juices",
                    "High-carb foods like porridge and bread",
                    "Boiled vegetables (Carrots, Radishes)",
                    "Strictly avoid oily, fried, and spicy foods"
                ]
            },
            "Arthritis": {
                "title": "Joint Health Diet",
                "tags": ["Anti-inflammatory", "Omega-3"],
                "details": [
                    "Fatty fish, walnuts, and flaxseeds",
                    "Olive oil for healthy oleocanthal",
                    "Rich in Vitamin C berries and citrus",
                    "Limit nighttime snacks and processed sugar"
                ]
            },
            "Migraine": {
                "title": "Trigger-Free Nutrition",
                "tags": ["Mg Rich", "Hydrating"],
                "details": [
                    "Magnesium-rich spinach and pumpkin seeds",
                    "Riboflavin sources like eggs and lean meat",
                    "Stay consistently hydrated throughout the day",
                    "Avoid triggers like aged cheese, caffeine, and wine"
                ]
            },
            "Pneumonia": {
                "title": "Lung Recovery Diet",
                "tags": ["Protein Rich", "Immune Support"],
                "details": [
                    "High-protein soft foods (Lentils, Eggs)",
                    "Warm soups and broths for hydration",
                    "Vitamin C rich oranges and bell peppers",
                    "Small, frequent meals to save energy"
                ]
            },
            "Chicken Pox": {
                "title": "Skin Healing Support",
                "tags": ["Cooling", "Soft Foods"],
                "details": [
                    "Soft, cool foods like yogurt and mashed fruits",
                    "Vitamin A rich carrots and sweet potatoes",
                    "Coconut water for internal cooling",
                    "Avoid salty, spicy, or acidic (citrus) foods"
                ]
            },
            "UTI": {
                "title": "Urinary Flush Plan",
                "tags": ["Hydrating", "Alkaline"],
                "details": [
                    "Unsweetened cranberry juice",
                    "High water intake (3-4L daily)",
                    "Probiotic-rich yogurt and fermented foods",
                    "Avoid irritating caffeine and spicy foods"
                ]
            },
            "Hemorrhoids": {
                "title": "High-Fiber Relief",
                "tags": ["High Fiber", "Stool Softening"],
                "details": [
                    "Whole grains, oats, and bran",
                    "Legumes, beans, and plenty of vegetables",
                    "High-water content fruits (Pears, Melons)",
                    "Maintain extreme hydration for fiber efficacy"
                ]
            },
            "Peptic Ulcer Disease": {
                "title": "Stomach Soothe",
                "tags": ["Bland Diet", "Low Acid"],
                "details": [
                    "Fiber-rich carrots, broccoli, and leafy greens",
                    "Probiotics like kombucha and yogurt",
                    "Lean proteins (Chicken, Fish)",
                    "Avoid coffee, chocolate, and spicy peppers"
                ]
            },
            "Allergy": {
                "title": "Histamine Balance",
                "tags": ["Low Histamine", "Immune Support"],
                "details": [
                    "Quercetin-rich onions, apples, and berries",
                    "Vitamin C sources to stabilize histamines",
                    "Anti-inflammatory ginger and turmeric",
                    "Identify and strictly avoid trigger foods"
                ]
            },
            "Drug Reaction": {
                "title": "System Flush",
                "tags": ["Hydrating", "Bland Diet"],
                "details": [
                    "Increase water to flush the system",
                    "Simple, non-allergenic foods (Rice, Banana)",
                    "Anti-inflammatory cucumber and aloe juice",
                    "Discontinue the suspect drug as per doctor advice"
                ]
            },
            "Impetigo": {
                "title": "Skin Infection Recovery",
                "tags": ["Immune Boost", "Anti-bacterial"],
                "details": [
                    "Zinc-rich pumpkin seeds and lean meats",
                    "Vitamin C for skin repair (Guava, Citrus)",
                    "Probiotics to support immune response",
                    "Maintain hygiene and avoid processed sugar"
                ]
            },
            "Cervical Spondylosis": {
                "title": "Nerve & Bone Support",
                "tags": ["Calcium Rich", "Anti-inflammatory"],
                "details": [
                    "Calcium sources (Dairy, Fortified milks)",
                    "Magnesium-rich greens and whole grains",
                    "Omega-3 fatty fish to reduce inflammation",
                    "Vitamin D for calcium absorption"
                ]
            },
            "Varicose Veins": {
                "title": "Vascular Health Plan",
                "tags": ["Bioflavonoids", "High Fiber"],
                "details": [
                    "Bioflavonoid-rich berries and grapes",
                    "Fiber to prevent strain (Whole grains)",
                    "Rutin-rich buckwheat and apples",
                    "Vitamin E sources like almonds and oils"
                ]
            },
            "Common Cold": {
                "title": "Immune Shield",
                "tags": ["Vitamin C", "Warm Fluids"],
                "details": [
                    "Hot soups and herbal teas (Ginger, Honey)",
                    "Vitamin C rich citrus and peppers",
                    "Garlic for antimicrobial defense",
                    "Proper rest and continuous hydration"
                ]
            }
        }

        # Default fallback plan
        default_plan = {
            "title": "Balanced Recovery Bowl",
            "tags": ["Nutrient Dense", "Healing"],
            "details": [
                "Fresh seasonal vegetables and fruits",
                "Lean protein source (Chicken, Beans, or Eggs)",
                "Whole grains for sustained energy",
                "Proper hydration with 3L+ water daily"
            ]
        }

        recovery_data = RECOVERY_PLANS.get(disease, default_plan)

        return jsonify({
            'disease': disease,
            'confidence': confidence_pct,
            'original_input': symptoms,
            'recovery': recovery_data
        })
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Failed to process symptoms.'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    # Chatbot still uses LLM for general conversation
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'response': "Please say something!"})

    prompt = f"You are a helpful medical assistant named BioGen. User: {user_message} Assistant:"
    payload = {"inputs": prompt, "parameters": {"max_length": 150}}

    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        res_json = response.json()
        if 'error' in res_json:
            return jsonify({'response': "I'm occupied. Try again soon."})
        bot_response = res_json[0].get('generated_text', "I couldn't understand.")
        return jsonify({'response': bot_response})
    except:
        return jsonify({'response': "Connection issue."})

if __name__ == '__main__':
    app.run(debug=True)
