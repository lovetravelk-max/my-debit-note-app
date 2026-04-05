import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# Set Page Config
st.set_page_config(page_title="FHI Debit Note Generator", layout="centered")
st.title("Insurance Debit Note Generator")

# Sidebar for Key
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        # 1. Inputs
        billing_date = st.date_input("Billing Date", datetime.now())
        formatted_billing_date = billing_date.strftime("%d%m%Y")
        display_billing_date = billing_date.strftime("%d/%m/%Y")

        # Session State to prevent AI re-runs when editing
        ai_key = f"data_{uploaded_file.name}"
        if ai_key not in st.session_state:
            with st.spinner("AI is analyzing..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
                    prompt = "Extract: Insured Name, Insurer Name, Policy/Quotation No, Insurance Class, Policy Period, Location, and Premium. Provide ONLY the list. No intro sentences."
                    response = model.generate_content([prompt, pdf_data])
                    # Clean text immediately
                    st.session_state[ai_key] = response.text.replace("**", "").replace("Here is the extracted information:", "").strip()
                except Exception as e:
                    st.error(f"AI Error: {e}")
                    st.stop()

        # 2. Preview & Edit
        st.subheader("Preview & Edit Details")
        editable_details = st.text_area("Edit details below:", value=st.session_state[ai_key], height=220)
        
        # Filename Logic
        policy_no = "DEBIT_NOTE"
        for line in editable_details.split('\n'):
            if any(x in line for x in ["No", "Policy", "Quotation"]):
                policy_no = line.split(':')[-1].strip().replace("/", "_").replace("\\", "_")
                break

        # 3. PDF Generation Logic
        if st.button("🚀 Generate Final Debit Note"):
            try:
                pdf = FPDF()
                pdf.add_page()
                
                # Logo (95mm)
                try:
                    pdf.image("logo.png", 10, 8, 95) 
                except:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # Header (Top Right)
                pdf.set_font("Arial", '', 9)
                pdf.set_xy(110, 10)
                pdf.cell(90, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
                pdf.set_x(110)
                pdf.cell(90, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.set_x(110)
                pdf.cell(90, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
                pdf.ln(18)
                
                # Title
                pdf.set_font("Arial", 'B', 22)
                pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
                pdf.ln(3)

               # --- CORRECTED POLICY DETAILS BOX ---
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, "  POLICY DETAILS", ln=True, fill=True)
                pdf.set_font("Arial", '', 10)
                
                pdf.ln(2) # Small gap after header
                
                for line in editable_details.split('\n'):
                    if line.strip():
                        # Clean the text for PDF encoding
                        pdf_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                        
                        # FIX: We set the width to 180mm to give it plenty of room to wrap
                        # This prevents the "Not enough horizontal space" error
                        pdf.set_x(15) # Slight indent for neatness
                        pdf.multi_cell(180, 6, pdf_line, align='L') 
                
                pdf.ln(8)

                # Payment Options (Reverted Font/Spacing)
                pdf.set_font("Arial", 'B', 11)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 8, "PREMIUM ARRANGEMENT OPTIONS:", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "1) CHEQUE", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(0, 5, "Payable to: FU HOI INSURANCE MANAGEMENT LIMITED\nMail to: Room 1229, 12/F., Beverley Commercial Centre, 87-105 Chatham Road, Tsim Sha Tsui.")
                pdf.ln(2)

                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "2) INTERNET BANKING (OCBC Wing Hang Bank - 035)", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(0, 5, "A/C Name: FU HOI INSURANCE MANAGEMENT LIMITED\nA/C No: 802 - 155874 - 831\n*Please email remittance slip to info@fhi.com.hk")
                pdf.ln(2)

                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "3) FPS", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "Mobile Number: +852 5622 2792", ln=True)
                
                # Date (Bottom Left)
                pdf.set_xy(10, 260)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 5, f"Billing Date: {display_billing_date}", ln=False)

                # Chop (30mm) & Signature
                try:
                    pdf.image("chop.png", 155, 230, 30) 
                except:
                    pass
                
                pdf.set_xy(140, 270)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Download Button with Unique Key to fix the Duplicate ID Error
                final_filename = f"{policy_no} {formatted_billing_date} DN.pdf"
                pdf_bytes = bytes(pdf.output())
                st.download_button(
                    label=f"💾 Download: {final_filename}", 
                    data=pdf_bytes, 
                    file_name=final_filename, 
                    mime="application/pdf",
                    key="final_download_btn"  # Unique ID added here
                )

            except Exception as e:
                st.error(f"Generation Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar.")
