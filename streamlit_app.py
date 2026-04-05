import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

st.set_page_config(page_title="FHI Debit Note Generator", layout="centered")
st.title("Insurance Debit Note Generator")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        st.info("AI is analyzing the document...")
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
            
            # Added "Insurer Name" to the extraction
            prompt = "Extract these fields: Insured Name, Insurer Name, Insurance Class, Policy Period, Location, and Premium. Return as a clean list without any ** symbols."
            
            response = model.generate_content([prompt, pdf_data])
            
            # --- PREVIEW & EDIT SECTION ---
            st.subheader("Preview & Edit Details")
            st.write("You can edit the text below before generating the final PDF:")
            
            # We clean the AI text to remove any ** formatting automatically
            clean_text = response.text.replace("**", "")
            editable_details = st.text_area("Final Content", value=clean_text, height=250)
            
            # --- PROFESSIONAL DEBIT NOTE DESIGN ---
            if st.button("🚀 Generate Final Debit Note"):
                pdf = FPDF()
                pdf.add_page()
                
                # 1. Logo (Enlarged to 50mm)
                try:
                    pdf.image("logo.png", 10, 8, 50) 
                except:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # 2. Company Header Info
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
                pdf.cell(0, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.cell(0, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
                pdf.ln(8) # Reduced spacing
                
                # 3. Title
                pdf.set_font("Arial", 'B', 20)
                pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
                pdf.ln(2)

                # 4. Extracted Policy Data Box
                pdf.set_font("Arial", 'B', 11)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, "  POLICY DETAILS", ln=True, fill=True)
                
                pdf.set_font("Arial", '', 10)
                # Use the edited text from the text area
                lines = editable_details.split('\n')
                for line in lines:
                    if line.strip():
                        # Standardizing symbols for PDF
                        pdf_line = line.strip().replace('•', '-').encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(0, 7, f"  {pdf_line}", ln=True)
                
                pdf.ln(5) # Reduced spacing to keep on one page

                # 5. Payment Methods
                pdf.set_font("Arial", 'B', 10)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 7, "PREMIUM ARRANGEMENT OPTIONS:", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "1) CHEQUE: Payable to FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.set_font("Arial", 'I', 8)
                pdf.multi_cell(0, 4, "Mail to: Room 1229, 12/F., Beverley Commercial Centre, 87-105 Chatham Road, Tsim Sha Tsui.")
                pdf.ln(2)

                pdf.set_font("Arial", '', 9)
                pdf.cell(0, 5, "2) INTERNET BANKING: OCBC Wing Hang Bank (035) A/C: 802-155874-831", ln=True)
                pdf.cell(0, 5, "   Account Name: FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)
                pdf.ln(2)

                pdf.cell(0, 5, "3) FPS: Mobile Number +852 5622 2792", ln=True)
                
                # 6. Signature & Chop (Moved up to avoid 2nd page)
                current_y = pdf.get_y()
                if current_y > 230: # Safety check
                    pdf.add_page()
                    current_y = 20
                
                try:
                    pdf.image("chop.png", 145, 220, 45) # Sized and positioned
                except:
                    pdf.set_xy(140, 250)
                    pdf.cell(0, 10, "__________________________", ln=True, align='R')
                
                pdf.set_xy(140, 265)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Final Save
                pdf_output = bytes(pdf.output())
                st.download_button(
                    label="💾 Download Final PDF", 
                    data=pdf_output, 
                    file_name="FHI_Debit_Note.pdf", 
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar.")
