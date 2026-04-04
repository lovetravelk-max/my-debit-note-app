import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

st.title("Insurance Debit Note Generator")

# Enter your API Key in the sidebar
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        st.info("Reading document...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # This prompt tells the AI exactly what you need
        prompt = "Extract from this insurance document: Insured Name, Class, Period, Location, and Premium. Format as a list."
        
        # Logic to send file to AI
        content = [{"mime_type": "application/pdf", "data": uploaded_file.getvalue()}, prompt]
        response = model.generate_content(content)
        
        st.subheader("Extracted Details")
        st.write(response.text)
        
        if st.button("Download Debit Note PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="DEBIT NOTE", ln=True, align='C')
            pdf.multi_cell(0, 10, txt=response.text)
            pdf.output("debit_note.pdf")
            st.success("Debit Note Ready!")
