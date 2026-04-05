import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="FHI Debit Note Generator", layout="centered")
st.title("Insurance Debit Note Generator")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        billing_date = st.date_input("Billing Date", datetime.now())
        formatted_billing_date = billing_date.strftime("%d%m%Y")
        display_billing_date = billing_date.strftime("%d/%m/%Y")

        st.info("AI is analyzing the document...")
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            
            # Refined prompt to remove intro text and extract clean data
            prompt = """Extract these fields: Insured Name, Insurer Name, Policy/Quotation No, 
            Insurance Class, Policy Period, Location, and Premium. 
            Provide ONLY the list. Do not include any introductory sentences like 'Here is the extracted information'."""
            
            response = model.generate_content([prompt, pdf_data])
            
            # --- PREVIEW & EDIT SECTION ---
            st.subheader("Preview & Edit Details")
            # Automatically strip unwanted markers and intro phrases
            clean_text = response.text.replace("**", "").replace("Here is the extracted information:", "").strip()
            editable_details = st.text_area("Edit details below:", value=clean_text, height=220)
            
            # Logic for Dynamic Filename
            policy_no = "DEBIT_NOTE"
            for line in editable_details.split('\n'):
                if any(x in line for x in ["No", "Policy", "Quotation"]):
                    policy_no = line.split(':')[-1].strip().replace("/", "_")
                    break

            # --- PDF GENERATION ---
            if st.button("🚀 Generate Final Debit Note"):
                pdf = FPDF()
                pdf.add_page()
                
                # 1. LARGE Logo (Increased to 75mm)
                try:
                    pdf.image("logo.png", 10, 8, 75) 
                except:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # 2. Company Header & Billing Date (Same Line)
                pdf.set_font("Arial", '', 9)
                pdf.set_xy(100, 8) # Position for address
                pdf.cell(100, 5, f"Room 1229, 12/F., Beverley Commercial Centre,   Date: {display_billing_date}", ln=True, align='R')
                pdf.set_x(100)
                pdf.cell(100, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.set_x(100)
                pdf.cell(100, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
                
                pdf.ln(15)
                
                # 3. Title
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
                pdf.ln(2)

                # 4. Data Box
                pdf.set_font("Arial", 'B', 11)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, "  POLICY DETAILS", ln=True, fill=True)
                
                pdf.set_font("Arial", '', 10)
                lines = editable_details.split('\n')
                for line in lines:
                    if line.strip():
                        pdf_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(0, 7, f"  {pdf_line}", ln=True)
                
                # ADD SPACE BEFORE PAYMENT OPTIONS
                pdf.ln(12) 

                # 5. Payment Methods
                pdf.set_font("Arial", 'B', 11)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 8, "PREMIUM ARRANGEMENT OPTIONS:", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 6, "1) CHEQUE: Payable to FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.set_font("Arial", 'I', 9)
                pdf.multi_cell(0, 5, "   Mail to: Room 1229, 12/F., Beverley Commercial Centre, 87-105 Chatham Road, Tsim Sha Tsui.")
                pdf.ln(2)

                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 6, "2) INTERNET BANKING: OCBC Wing Hang Bank (035) A/C: 802-155874-831", ln=True)
                pdf.cell(0, 6, "   Account Name: FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.ln(2)

                pdf.cell(0, 6, "3) FPS: Mobile Number +852 5622 2792", ln=True)
                
                # 6. Signature & Chop Placement (Ensuring 1-page fit)
                try:
                    pdf.image("chop.png", 145, 225, 45) 
                except:
                    pass
                
                pdf.set_xy(140, 270)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Dynamic Filename
                final_filename = f"{policy_no} {formatted_billing_date} DN.pdf"
                
                pdf_output = bytes(pdf.output())
                st.download_button(
                    label=f"💾 Download: {final_filename}", 
                    data=pdf_output, 
                    file_name=final_filename, 
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar.")
