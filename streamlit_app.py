import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

st.set_page_config(page_title="Debit Note Generator", layout="centered")
st.title("Insurance Debit Note Generator")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        # This is where the indentation matters! 
        # Everything below is pushed to the right.
        st.info("Reading document...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            prompt = "Extract: Insured Name, Insurance Class, Policy Period, Location, and Premium. Format as a simple list."
            
            response = model.generate_content([prompt, pdf_data])
            
            st.subheader("Extracted Details")
            st.write(response.text)
            
            # This button will eventually create the pretty PDF
            if st.button("Download Debit Note"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="INSURANCE DEBIT NOTE", ln=True, align='C')
                pdf.ln(10)
                pdf.multi_cell(0, 10, txt=response.text)
                
                # Save the PDF
                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button(label="Click here to save PDF", data=pdf_output, file_name="Debit_Note.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to start.")
