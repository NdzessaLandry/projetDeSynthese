import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
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


# --- Model Loading ---
@st.cache_resource
def load_my_model():
    try:
        model = load_model('medical_multi_task_model.h5')
        return model
    except Exception as e:
        st.error(T("radio_model_error").format(e=e))
        return None

# --- Page Content ---
st.title(T("radio_title"))
st.markdown(T("radio_intro"))

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader(T("radio_uploader"), type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption=T("radio_uploaded_caption"), use_column_width=True)

    with col2:
        if uploaded_file is not None:
            st.subheader(T("radio_results_title"))
            with st.spinner(T("radio_spinner")):
                model = load_my_model()

                if model is None:
                    st.warning(T("radio_model_not_loaded"))
                else:
                    # Preprocess, predict, interpret...
                    img_array = np.array(image.convert('RGB').resize((224, 224)))
                    img_array = img_array / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    predictions = model.predict(img_array)

                    disease_pred_proba = predictions[0][0][0]
                    sex_pred_proba = predictions[1][0][0]
                    age_pred_value = int(predictions[2][0][0])

                    disease_status = T("disease_status_sick") if disease_pred_proba > 0.5 else T("disease_status_normal")
                    sex_status = T("sex_female") if sex_pred_proba > 0.5 else T("sex_male")

                    analysis_data = {
                        "type": "Analyse Radiographique",
                        "image": image,
                        "disease_status": disease_status,
                        "sex_status": sex_status,
                        "age_pred_value": age_pred_value,
                        "disease_pred_proba": disease_pred_proba,
                        "sex_pred_proba": sex_pred_proba,
                        "raw_age_pred": predictions[2][0][0],
                        "timestamp": datetime.datetime.now()
                    }
                    st.session_state['last_radio_analysis'] = analysis_data
                    st.session_state['history'].append(analysis_data)
                    save_history()

                    # Display results
                    if disease_status == T("disease_status_sick"):
                        st.warning(f"{T('radio_disease_status')}: **{disease_status}**")
                    else:
                        st.success(f"{T('radio_disease_status')}: **{disease_status}**")

                    st.metric(label=T("radio_predicted_sex"), value=sex_status)
                    st.metric(label=T("radio_predicted_age"), value=f"{age_pred_value} ans")

                    with st.expander(T("radio_details_expander")):
                        st.write(f"{T('radio_proba_disease')}: {disease_pred_proba:.2f}")
                        st.write(f"{T('radio_proba_female')}: {sex_pred_proba:.2f}")
                        st.write(f"{T('radio_raw_age')}: {predictions[2][0][0]:.2f} ans")

                    pdf_bytes = generate_pdf_report(analysis_data)
                    st.download_button(
                        label=T("radio_download_pdf"),
                        data=pdf_bytes,
                        file_name=f"rapport_radiographie_{analysis_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )

            st.info(T("radio_analysis_done"))

# XAI Section outside the main columns to give it full width
if uploaded_file is not None: # Only show XAI if an image was uploaded
    st.markdown("---")
    with st.container():
        st.subheader(T("radio_xai_title"))
        st.info(T("radio_xai_info"))
        if st.button(T("radio_xai_button")):
            st.warning(T("radio_xai_in_dev"))