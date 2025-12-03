import streamlit as st
from PIL import Image

st.title("Uploader une radio")

file= st.file_uploader("Choisissez une image de radio à uploader", type=["png", "jpg", "jpeg"])
if file is not None:
    image = Image.open(file)
    st.image(image, caption='Image uploadée avec succès.', use_column_width=True)
    st.write("")
    st.write("Analyse de l'image...")
    # Ici, vous pouvez ajouter le code pour analyser l'image uploadée
    st.success("Analyse terminée!")
    