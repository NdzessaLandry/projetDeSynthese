import streamlit as st
import datetime
from pdf_generator import generate_pdf_report
from history_manager import save_history

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
T = get_text


# --- Page Content ---
import streamlit as st
import datetime
from pdf_generator import generate_pdf_report
from history_manager import save_history

# --- Authentication Check ---
if not st.session_state.get("authentication_status"):
    st.error("Veuillez vous connecter pour accéder à cette page. / Please log in to access this page.")
    st.stop()

# --- Translation Setup (only if authenticated) ---
from app import get_text
T = get_text

# --- Initialize form step ---
if 'symptom_form_step' not in st.session_state:
    st.session_state.symptom_form_step = 0

# --- Page Content ---
st.title(T("symptoms_title"))
st.markdown(T("symptoms_intro"))

with st.container(): # Main container for the form
    if st.session_state.symptom_form_step == 0:
        st.subheader(T("symptoms_step1_title"))
        with st.form('basic_info_form'):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input(T("symptoms_age"), min_value=0, max_value=120, value=st.session_state.get('symptom_age', 30), help=T("symptoms_age_help"))
            with col2:
                weight = st.number_input(T("symptoms_weight"), min_value=0.0, max_value=300.0, value=st.session_state.get('symptom_weight', 70.0), help=T("symptoms_weight_help"))
            
            submit_basic_info = st.form_submit_button(label=T("symptoms_next_button"))
            if submit_basic_info:
                st.session_state.symptom_age = age
                st.session_state.symptom_weight = weight
                st.session_state.symptom_form_step = 1
                st.rerun()

    elif st.session_state.symptom_form_step == 1:
        st.subheader(T("symptoms_step2_title"))
        with st.form('symptoms_description_form'):
            symptoms = st.text_area(T("symptoms_description"), value=st.session_state.get('symptoms_text', ''), help=T("symptoms_description_help"))
            
            col_buttons = st.columns(2)
            with col_buttons[0]:
                back_button = st.form_submit_button(label=T("symptoms_back_button"))
                if back_button:
                    st.session_state.symptoms_text = symptoms
                    st.session_state.symptom_form_step = 0
                    st.rerun()
            with col_buttons[1]:
                submit_symptoms = st.form_submit_button(label=T("symptoms_submit_button"))
                if submit_symptoms:
                    st.session_state.symptoms_text = symptoms
                    st.session_state.symptom_form_step = 2
                    st.rerun()

    elif st.session_state.symptom_form_step == 2:
        st.subheader(T("symptoms_submitted_info"))
        st.write(f"**{T('symptoms_age')}:** {st.session_state.symptom_age} ans")
        st.write(f"**{T('symptoms_weight')}:** {st.session_state.symptom_weight} kg")
        st.write(f"**{T('symptoms_description')}:** {st.session_state.symptoms_text}")
        
        st.markdown("---")
        st.subheader(T("symptoms_results_title"))

        symptoms_lower = st.session_state.symptoms_text.lower()
        suspicious_keywords = ["fièvre", "douleur thoracique", "difficulté à respirer", "perte de conscience", "hémorragie", "fever", "chest pain", "difficulty breathing", "loss of consciousness", "hemorrhage"]
        found_keywords = [word for word in suspicious_keywords if word in symptoms_lower]
        
        analysis_result = {
            "found_keywords": found_keywords,
            "recommendation": ""
        }

        if found_keywords:
            recommendation = T("symptoms_keywords_found").format(keywords=', '.join(found_keywords))
            analysis_result["recommendation"] = recommendation
            st.warning(recommendation)
        else:
            recommendation = T("symptoms_no_keywords")
            analysis_result["recommendation"] = recommendation
            st.success(recommendation)
        
        analysis_data = {
            "type": "Analyse de Symptômes",
            "age": st.session_state.symptom_age,
            "weight": st.session_state.symptom_weight,
            "symptoms": st.session_state.symptoms_text,
            "analysis": analysis_result,
            "timestamp": datetime.datetime.now()
        }
        st.session_state['last_symptom_analysis'] = analysis_data
        st.session_state['history'].append(analysis_data)
        save_history()
        
        pdf_bytes = generate_pdf_report(analysis_data)
        st.download_button(
            label=T("radio_download_pdf"),
            data=pdf_bytes,
            file_name=f"rapport_symptomes_{analysis_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
        st.markdown("---")
        if st.button(T("symptoms_start_new_button")):
            st.session_state.symptom_form_step = 0
            st.session_state.symptom_age = 30
            st.session_state.symptom_weight = 70.0
            st.session_state.symptoms_text = ''
            st.rerun()