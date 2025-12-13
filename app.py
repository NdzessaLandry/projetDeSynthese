import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from history_manager import load_history, save_history
from locales import TEXTS

# --- PAGE CONFIG (doit être la première commande st) ---
st.set_page_config(
    page_title="Medical Diagnosis App",
    page_icon="🩺",
    layout="wide"
)

# --- Inject custom CSS ---
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialisation de l'état de la session (doit être au début du script principal)
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'fr' # Langue par défaut
if 'history' not in st.session_state:
    st.session_state['history'] = [] # Sera chargé après authentification
if 'last_radio_analysis' not in st.session_state:
    st.session_state['last_radio_analysis'] = None
if 'last_symptom_analysis' not in st.session_state:
    st.session_state['last_symptom_analysis'] = None

# --- AUTHENTICATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Check if user is already logged in
if st.session_state.get("authentication_status"):
    # --- LANGUAGE SELECTION (pour utilisateurs authentifiés) ---
    st.sidebar.selectbox("Langue / Language", options=['fr', 'en'], key='lang')

    # Fonction pour obtenir le texte localisé
    def get_text(key):
        return TEXTS[st.session_state['lang']][key]
    T = get_text # Alias pour un accès plus court

    # --- APP LOGIC (if already authenticated) ---
    name = st.session_state['name']
    
    # Charger l'historique une fois l'utilisateur authentifié
    if not st.session_state['history']: # Charger seulement si l'historique est vide ou n'a pas été chargé pour cet user
        st.session_state['history'] = load_history()

    # Sidebar
    st.sidebar.title(f"{T('sidebar_welcome')} {name}")
    authenticator.logout(T('sidebar_logout'), 'sidebar')
    st.sidebar.markdown("---")
    st.sidebar.title(T("sidebar_title"))
    st.sidebar.markdown(T("sidebar_intro"))
    st.sidebar.info(T("sidebar_warning"))

    # Main page
    st.markdown(f'<div class="main-welcome-section"><h1>{T("welcome_title")}</h1><p>{T("welcome_message")}</p></div>', unsafe_allow_html=True)


else:
    # --- LANGUAGE SELECTION (pour écran de connexion/inscription) ---
    # Ici, nous utilisons une version simplifiée de T pour éviter les erreurs avant l'authentification
    # Le sélecteur de langue sera affiché mais ne mettra pas à jour st.session_state['lang'] directement
    # car la fonction get_text n'est pas encore définie dans ce scope
    # Pour l'écran de connexion/inscription, nous utiliserons des textes hardcodés ou une version simple de T
    st.sidebar.selectbox("Langue / Language", options=['fr', 'en'], key='lang_unauthenticated') # Utilisez une clé différente

    def get_text_unauthenticated(key):
        # Assure that 'lang_unauthenticated' is initialized
        if 'lang_unauthenticated' not in st.session_state:
            st.session_state['lang_unauthenticated'] = 'fr'
        return TEXTS[st.session_state['lang_unauthenticated']][key]
    T_unauthenticated = get_text_unauthenticated

    # --- LOGIN / REGISTER UI ---
    choice = st.selectbox(T_unauthenticated("register_select_option"), ['Login', 'Register'])

    if choice == 'Login':
        name, authentication_status, username = authenticator.login(T_unauthenticated("login_button"), 'main')
        
        if authentication_status == False:
            st.error(T_unauthenticated('login_error'))
        elif authentication_status == None:
            st.warning(T_unauthenticated('login_warning'))
        elif authentication_status == True:
            st.session_state['lang'] = st.session_state['lang_unauthenticated'] # Synchronize lang after login
            st.rerun() # Rerun the script to enter the main app logic

    elif choice == 'Register':
        try:
            if authenticator.register_user(T_unauthenticated('register_button'), 'main', preauthorization=False):
                st.success(T_unauthenticated('register_success_message'))
                # Save the updated config
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.info(T_unauthenticated('register_info_message'))
        except Exception as e:
            st.error(e)