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
            model = genai.GenerativeModel('gemini-2.5-flash')
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            prompt = "Extract: Insured Name, Insurance Class, Policy Period, Location, and Premium. Format as a simple list."
            
            response = model.generate_content([prompt, pdf_data])
            
            st.subheader("Extracted Details")
            st.write(response.text)
            
           # --- PROFESSIONAL DEBIT NOTE DESIGN ---
            if st.button("Download Professional Debit Note"):
                pdf = FPDF()
                pdf.add_page()
                
                # 1. Logo (Looks for logo.png in your GitHub)
                try:
                    pdf.image("logo.png", 10, 8, 33)
                except:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # 2. Company Header Info
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
                pdf.cell(0, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.cell(0, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
                pdf.ln(10)
                
                # 3. Title
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
                pdf.ln(5)

                # 4. Extracted Policy Data
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 10, "  POLICY DETAILS", ln=True, fill=True)
                
                pdf.set_font("Arial", '', 11)
                lines = response.text.split('\n')
                for line in lines:
                    if line.strip():
                        # Cleaning text for PDF compatibility
                        clean_line = line.strip().replace('•', '-').encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(0, 8, f"  {clean_line}", ln=True)
                
                pdf.ln(10)

                # 5. Your Specific Payment Methods
                pdf.set_font("Arial", 'B', 11)
                pdf.set_text_color(0, 51, 102) # Dark Blue for Payment Section
                pdf.cell(0, 8, "PREMIUM ARRANGEMENT OPTIONS:", ln=True)
                pdf.set_text_color(0, 0, 0) # Back to Black
                
                pdf.set_font("Arial", '', 9)
                # Option 1: Cheque
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "1) CHEQUE", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(0, 5, "Payable to: FU HOI INSURANCE MANAGEMENT LIMITED\nMail to: Room 1229, 12/F., Beverley Commercial Centre, 87-105 Chatham Road, Tsim Sha Tsui.")
                pdf.ln(2)

                # Option 2: Internet Banking
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "2) INTERNET BANKING (OCBC Wing Hang Bank - 035)", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(0, 5, "A/C Name: FU HOI INSURANCE MANAGEMENT LIMITED\nA/C No: 802 - 155874 - 831\n*Please email remittance slip to info@fhi.com.hk")
                pdf.ln(2)

                # Option 3: FPS
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 5, "3) FPS", ln=True)
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "Mobile Number: +852 5622 2792", ln=True)
                
                # 6. Company Chop Placement
                try:
                    pdf.image("chop.png", 150, 235, 40)
                except:
                    pdf.ln(15)
                    pdf.cell(0, 10, "__________________________", ln=True, align='R')
                
                pdf.set_xy(140, 275)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Final Save and Download
                pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
                st.download_button(
                    label="🚀 Generate Professional Debit Note", 
                    data=pdf_output, 
                    file_name="FHI_Debit_Note.pdf", 
                    mime="application/pdf"
                )
                
                # Final Save and Download (Fixed Version)
                try:
                    # We use 'output()' directly for the data
                    pdf_data_output = pdf.output()
                    
                    st.download_button(
                        label="🚀 Generate Professional Debit Note", 
                        data=pdf_data_output, 
                        file_name="FHI_Debit_Note.pdf", 
                        mime="application/pdf"
                    )
                except Exception as pdf_err:
                    st.error(f"PDF Download Error: {pdf_err}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.warning("Please enter your Gemini API Key in the sidebar.")
