from fpdf import FPDF
from PIL import Image
import io

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Rapport de Diagnostic Médical', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, 'Avertissement: Ce rapport ne remplace pas un avis médical professionnel.', 0, 0, 'R')


def generate_pdf_report(analysis_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.set_auto_page_break(auto=True, margin=15) # Enable auto page break

    page_width = pdf.w - pdf.l_margin - pdf.r_margin # Calculate available page width
    
    timestamp = analysis_data.get('timestamp')
    if timestamp:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, f"Date de l'analyse : {timestamp.strftime('%d/%m/%Y %H:%M:%S')}", 0, 1)
        pdf.set_font('Arial', '', 12)

    pdf.ln(5)

    if analysis_data['type'] == 'Analyse Radiographique':
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, "Rapport d'Analyse Radiographique", 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Résultats :", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(page_width, 10, f"Statut de la maladie : {analysis_data['disease_status']}")
        pdf.multi_cell(page_width, 10, f"Âge prédit : {analysis_data['age_pred_value']} ans")
        pdf.multi_cell(page_width, 10, f"Sexe prédit : {analysis_data['sex_status']}")
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Image analysée :", 0, 1)
        
        # Save PIL image to a byte stream to be used by FPDF
        img_byte_arr = io.BytesIO()
        analysis_data['image'].save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Get image dimensions to scale it properly
        with Image.open(io.BytesIO(img_byte_arr)) as img:
            width, height = img.size
        
        aspect_ratio = height / width
        # Ensure image fits within page width
        image_w = 100
        image_h = image_w * aspect_ratio
        if image_w > page_width:
            image_w = page_width
            image_h = image_w * aspect_ratio

        pdf.image(io.BytesIO(img_byte_arr), x=pdf.get_x(), y=pdf.get_y(), w=image_w, h=image_h)
        pdf.ln(image_h + 5) # Advance y position after image

    elif analysis_data['type'] == 'Analyse de Symptômes':
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, "Rapport d'Analyse de Symptômes", 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Informations du patient :", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(page_width, 10, f"Âge : {analysis_data['age']} ans")
        pdf.multi_cell(page_width, 10, f"Poids : {analysis_data['weight']} kg")
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Symptômes décrits :", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(page_width, 10, analysis_data['symptoms'])
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Recommandation :", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(page_width, 10, analysis_data['analysis']['recommendation'])
        
    return pdf.output(dest='S').encode('latin-1')

