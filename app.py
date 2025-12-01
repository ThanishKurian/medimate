import streamlit as st
import pandas as pd

# --- Data Model ---
# In a real application, this would be a comprehensive database/JSON file
BODY_PART_SYMPTOMS = {
    "Head/Neck": [
        "Severe headache", "Dizziness", "Blurred vision", "Facial numbness", "Sore throat"
    ],
    "Chest/Back": [
        "Shortness of breath", "Chest pain", "Persistent cough", "Heart palpitations", "Upper back pain"
    ],
    "Abdomen/Pelvis": [
        "Sharp stomach pain", "Nausea/Vomiting", "Diarrhea", "Constipation", "Bloating", "Pelvic pain"
    ],
    "Joints/Limbs": [
        "Joint swelling", "Muscle weakness", "Numbness in limbs", "Severe cramping", "Foot tingling"
    ],
    "Systemic": [
        "Fever", "Fatigue", "Unexplained weight loss", "Night sweats"
    ],
}

DISEASE_PROFILES = {
    "Migraine": {"Severe headache": 0.95, "Blurred vision": 0.6, "Dizziness": 0.4},
    "Pneumonia": {"Persistent cough": 0.9, "Shortness of breath": 0.8, "Fever": 0.7},
    "Irritable Bowel Syndrome (IBS)": {"Sharp stomach pain": 0.7, "Bloating": 0.9, "Constipation": 0.5},
    "Anxiety Disorder": {"Heart palpitations": 0.8, "Shortness of breath": 0.5, "Dizziness": 0.5, "Fatigue": 0.6},
    "Rheumatoid Arthritis": {"Joint swelling": 0.9, "Joint stiffness": 0.8, "Fatigue": 0.5},
}
# --- Helper Functions ---

def calculate_probability(selected_symptoms):
    """Calculates the probability match for each disease."""
    if not selected_symptoms:
        return pd.DataFrame({'Disease': [], 'Probability': []})

    results = {}
    for disease, symptom_weights in DISEASE_PROFILES.items():
        match_score = 0
        max_possible_score = 0
        
        # Calculate match score based on selected symptoms
        for symptom in selected_symptoms:
            if symptom in symptom_weights:
                match_score += symptom_weights[symptom]
        
        # Calculate maximum possible score based on all symptoms the disease has
        for weight in symptom_weights.values():
             max_possible_score += weight
        
        # Avoid division by zero and ensure score is normalized
        if max_possible_score > 0:
            probability = (match_score / max_possible_score) * 100
            results[disease] = min(probability, 100) # Cap at 100%

    # Convert to DataFrame for display, filter out low matches, and sort
    df = pd.DataFrame(results.items(), columns=['Disease', 'Probability'])
    df = df.sort_values(by='Probability', ascending=False)
    # Filter to only show probabilities > 5%
    df = df[df['Probability'] > 5].head(5) 
    
    return df

# --- Streamlit App ---

st.set_page_config(
    page_title="Interactive Symptom Checker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing selected symptoms
if 'selected_symptoms' not in st.session_state:
    st.session_state['selected_symptoms'] = set()
if 'current_part' not in st.session_state:
    st.session_state['current_part'] = list(BODY_PART_SYMPTOMS.keys())[0]

# --- Title and Instructions ---
st.title("Interactive Symptom Checker 🧑‍⚕️")
st.markdown("Use the controls below to select your symptoms from a realistic human silhouette model (simulated using buttons).")

# --- Layout: Body Model (Simulated) and Symptom Checklist ---
col_model, col_symptoms = st.columns([1, 2])

with col_model:
    st.header("1. Select Body Part")
    st.markdown("**(Simulated Clickable 3D Model)**")
    
    # Use a placeholder image for a human figure silhouette
    st.image("https://i.imgur.com/k9vR2rM.png", use_column_width=True, caption="Clickable Human Silhouette Placeholder")
    st.markdown("---")

    # Body Part Selection (Simulating the 'Click' on the body)
    st.subheader("Click on a Part to View Symptoms:")
    
    # Use radio buttons for the most realistic 'single-click' feeling
    selected_part_via_ui = st.radio(
        label="Choose a body area:",
        options=list(BODY_PART_SYMPTOMS.keys()),
        index=list(BODY_PART_SYMPTOMS.keys()).index(st.session_state.current_part),
        key="body_part_radio"
    )
    st.session_state.current_part = selected_part_via_ui


with col_symptoms:
    st.header(f"2. Select Symptoms for **{st.session_state.current_part}**")
    
    symptoms_for_part = BODY_PART_SYMPTOMS.get(st.session_state.current_part, [])
    
    # Create the checklist for symptoms
    new_selections = st.multiselect(
        label=f"Select all symptoms you are experiencing in the {st.session_state.current_part} area:",
        options=symptoms_for_part,
        default=list(st.session_state.selected_symptoms.intersection(set(symptoms_for_part))),
        key="symptom_multiselect"
    )

    # Update the overall symptom list using session state
    # First, remove symptoms from the current part that are NOT in new_selections
    st.session_state.selected_symptoms.difference_update(set(symptoms_for_part) - set(new_selections))
    # Then, add the newly selected symptoms
    st.session_state.selected_symptoms.update(new_selections)

# --- Display Symptoms & Prediction ---
st.markdown("---")
st.header("3. Diagnosis Prediction")

if not st.session_state.selected_symptoms:
    st.info("Please select symptoms from the body model (left side) to see a prediction.")
else:
    # Display the current list of symptoms
    st.subheader("Your Current Symptoms:")
    st.markdown(f"**Total Symptoms Selected:** **{len(st.session_state.selected_symptoms)}**")
    st.markdown(f"> *{', '.join(sorted(list(st.session_state.selected_symptoms)))}*")
    
    st.markdown("---")
    
    # Run the prediction
    prediction_df = calculate_probability(st.session_state.selected_symptoms)
    
    st.subheader("Likely Conditions (Based on Symptom Match)")
    
    if prediction_df.empty:
        st.warning("No known conditions match your current symptom profile with high confidence.")
    else:
        # Display results with probability bars
        for index, row in prediction_df.iterrows():
            disease = row['Disease']
            prob = row['Probability']
            
            # Use columns for a clean display
            col_name, col_bar, col_prob = st.columns([2, 5, 1])
            
            with col_name:
                st.markdown(f"**{disease}**")
            
            with col_bar:
                # Progress bar visualization
                st.progress(prob / 100)
            
            with col_prob:
                st.markdown(f"**{prob:.1f}%**")

st.markdown("---")
st.caption("Disclaimer: This tool is for informational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment.")

# To run this:
# 1. Save the code as app.py
# 2. Find a simple human silhouette image (like the one I linked: https://i.imgur.com/k9vR2rM.png)
# 3. Run: streamlit run app.py
