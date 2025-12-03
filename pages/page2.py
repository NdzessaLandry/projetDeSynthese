import streamlit as st

st.title("Entrer des informations médicales")

with st.form('medical_info_form'):
    age = st.number_input("Âge", min_value=0, max_value=120, value=30)
    weight = st.number_input("Poids (kg)", min_value=0.0, max_value=300.0, value=70.0)
    symptoms = st.text_area("Décrivez vos symptômes")
    
    submit_button = st.form_submit_button(label='Soumettre')
    if submit_button:
        st.write("Informations soumises avec succès!")
        st.write(f"Âge: {age}")
        st.write(f"Poids: {weight} kg")
        st.write(f"Symptômes: {symptoms}")