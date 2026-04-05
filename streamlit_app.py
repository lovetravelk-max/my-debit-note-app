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
        # 1. NEW: Billing Date Selector (Defaults to today)
        billing_date = st.date_input("Billing Date", datetime.now())
        formatted_billing_date = billing_date.strftime("%d%m%Y")
        display_billing_date = billing_date.strftime("%d/%m/%Y")

        st.info("AI is analyzing the document...")
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            
            # Updated prompt to include Insurer and Policy No
            prompt = """Extract these fields: Insured Name, Insurer Name, Policy/Quotation No, 
            Insurance Class, Policy Period, Location, and Premium. 
            Return as a clean list without any ** symbols."""
            
            response = model.generate_content([prompt, pdf_data])
            
            # --- PREVIEW & EDIT SECTION ---
            st.subheader("Preview & Edit Details")
            clean_text = response.text.replace("**", "")
            editable_details = st.text_area("Edit details below:", value=clean_text, height=250)
            
            # 2. NEW: Extract Policy No for the Filename
            # We look for a line starting with 'Policy' or 'Quotation' in your edit box
            policy_no = "DEBIT_NOTE"
            for line in editable_details.split('\n'):
                if "No" in line or "Policy" in line or "Quotation" in line:
                    policy_no = line.split(':')[-1].strip().replace("/", "_") # Clean for filename
                    break

            # --- PDF GENERATION ---
            if st.button("🚀 Generate Final Debit Note"):
                pdf = FPDF()
                pdf.add_page()
                
                # 1. Logo (Large size)
                try:
                    pdf.image("logo.png", 10, 8, 55) 
                except:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # 2. Company Header & Billing Date
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
                pdf.cell(0, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.cell(0, 5, f"Billing Date: {display_billing_date}", ln=True, align='R')
                pdf.ln(8)
                
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
                
                pdf.ln(5)

                # 5. Payment Methods (Condensed to stay on one page)
                pdf.set_font("Arial", 'B', 10)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 7, "PREMIUM ARRANGEMENT OPTIONS:", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "1) CHEQUE: Payable to FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.set_font("Arial", 'I', 8)
                pdf.multi_cell(0, 4, "Mail to: Room 1229, 12/F., Beverley Commercial Centre, 87-105 Chatham Road, Tsim Sha Tsui.")
                pdf.ln(1)

                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, f"2) INTERNET BANKING: OCBC Wing Hang Bank (035) A/C: 802-155874-831", ln=True)
                pdf.cell(0, 5, "   A/C Name: FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.ln(1)

                pdf.cell(0, 5, "3) FPS: Mobile Number +852 5622 2792", ln=True)
                
                # 6. Signature & Chop Placement
                try:
                    pdf.image("chop.png", 145, 225, 45) 
                except:
                    pass
                
                pdf.set_xy(140, 270)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Dynamic Filename Logic
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
