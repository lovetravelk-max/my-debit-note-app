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
        try:
            # 1. Setup the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 2. Prepare the file and the question
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            prompt = "Extract these 5 fields from the document: Insured Name, Insurance Class, Policy Period, Location, and Premium. Return them as a clear list."
            
            # 3. Ask the AI
            response = model.generate_content([prompt, pdf_data])
            
            # 4. Show the results
            st.subheader("Extracted Details")
            st.write(response.text)
            
            # Save the text for the PDF generator
            st.session_state['extracted_text'] = response.text

        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.info("Tip: Double-check that your Gemini API Key is pasted correctly in the sidebar.")
        
        if st.button("Download Debit Note PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="DEBIT NOTE", ln=True, align='C')
            pdf.multi_cell(0, 10, txt=response.text)
            pdf.output("debit_note.pdf")
            st.success("Debit Note Ready!")
