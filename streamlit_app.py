import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# Set Page Config
st.set_page_config(page_title="FHI Debit Note Generator", layout="centered", page_icon="📝")
st.title("Insurance Debit Note Generator")

# Sidebar for Key
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    uploaded_file = st.file_uploader("Upload Policy/Quotation (PDF)", type="pdf")

    if uploaded_file:
        # Billing Date Input
        billing_date = st.date_input("Billing Date", datetime.now())
        formatted_billing_date = billing_date.strftime("%d%m%Y")
        display_billing_date = billing_date.strftime("%d/%m/%Y")

        # Create unique keys for session state management
        ai_response_key = f"{uploaded_file.name}_ai_response"
        editable_text_key = f"{uploaded_file.name}_editable_text"

        # --- AI EXTRACTION PHASE (Only run once per upload) ---
        # FIX: The condition below stops AI re-runs when editing/downloading
        if ai_response_key not in st.session_state:
            with st.spinner("AI is analyzing the document..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    pdf_data = {'mime_type': 'application/pdf', 'data': uploaded_file.getvalue()}
                    
                    # Refined prompt for clean data extraction
                    prompt = """Extract these fields clearly: Insured Name, Insurer Name, Policy/Quotation No, 
                    Insurance Class, Policy Period, Location, and Premium. 
                    Provide ONLY the list. Do not include introductory sentences."""
                    
                    response = model.generate_content([prompt, pdf_data])
                    
                    # Clean and store the text in session state
                    clean_text = response.text.replace("**", "").replace("Here is the extracted information:", "").strip()
                    st.session_state[ai_response_key] = clean_text
                    
                except Exception as e:
                    st.error(f"AI Extraction Error: {e}")
                    st.stop() # Stop if AI fails

        # --- PREVIEW & EDIT SECTION ---
        st.subheader("Preview & Edit Details")
        st.markdown("_If you edit the text box below, your changes will be used to generate the final PDF._")
        
        # Use the stored AI text as the default value
        default_edit_text = st.session_state.get(ai_response_key, "")
        
        # We use standard text_area which now persists because AI doesn't re-run
        editable_details = st.text_area("Edit details below (e.g., delete 'Anywhere within HK'):", value=default_edit_text, height=250)
        
        # Filename Logic (Searches the edited text)
        policy_no = "DEBIT_NOTE"
        for line in editable_details.split('\n'):
            if any(x in line for x in ["No", "Policy", "Quotation"]):
                policy_no = line.split(':')[-1].strip().replace("/", "_").replace("\\", "_")
                break

        # --- PDF GENERATION PHASE ---
        if st.button("🚀 Generate Final Debit Note"):
            pdf = FPDF()
            pdf.add_page()
            
            # 1. LOGO: BIGGER (Set to 95mm width)
            try:
                pdf.image("logo.png", 10, 8, 95) 
            except:
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

            # 2. Company Header (Top Right)
            pdf.set_font("Arial", '', 9)
            pdf.set_xy(110, 10)
            pdf.cell(90, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
            pdf.set_x(110)
            pdf.cell(90, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
            pdf.set_x(110)
            pdf.cell(90, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
            
            # Add breathing room after the header
            pdf.ln(18)
            
            # 3. Title
            pdf.set_font("Arial", 'B', 22)
            pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
            pdf.ln(3)

            # 4. Policy Data Box (Persistent Spacing)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(240, 240, 240) # Light Gray Fill
            pdf.cell(0, 8, "  POLICY DETAILS", ln=True, fill=True)
            
            # Reset font for details
            pdf.set_font("Arial", '', 10)
            
            # Use the edited text from the text_area
            # FPDF uses multi_cell for wrapping long text
            lines = editable_details.split('\n')
            for line in lines:
                if line.strip():
                    # Sanitize text for standard PDF encoding
                    pdf_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                    # We use multi_cell with a small height so it wraps automatically
                    pdf.multi_cell(0, 6, f"  {pdf_line}") 
            
            # Persistent Spacing before Payment Section
            pdf.ln(12) 

            # 5. Payment Methods (REVERTED TO VERSION YOU LIKED)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 51, 102) # Dark Blue Header
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
            
            # 6. Chop and Signature Area (Moved further down to fill the page)
            try:
                # CHOP: SMALLER (Reduced to 30mm width, repositioned)
                pdf.image("chop.png", 155, 235, 30) 
            except:
                pass # Skip silently if chop is missing
            
            # Final Signature Line at the very bottom
            pdf.set_xy(140, 270)
            pdf.set_font("Arial", 'I', 9)
            pdf.cell(60, 5, "Authorized Signature", align='C')

            # Dynamic Filename and Download
            final_filename = f"{policy_no} {formatted_billing_date} DN.pdf"
            
            # Final conversion for download
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label=f"💾 Download Final: {final_filename}", 
                data=pdf_bytes, 
                file_name=final_filename, 
                mime="application/pdf"
            )

       # --- PDF GENERATION PHASE ---
        if st.button("🚀 Generate Final Debit Note"):
            try:
                pdf = FPDF()
                pdf.add_page()
                
                # 1. LOGO: BIGGER (95mm)
                try:
                    pdf.image("logo.png", 10, 8, 95) 
                except:
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, "FU HOI INSURANCE MANAGEMENT LIMITED", ln=True)

                # 2. Company Header (Top Right)
                pdf.set_font("Arial", '', 9)
                pdf.set_xy(110, 10)
                pdf.cell(90, 5, "Room 1229, 12/F., Beverley Commercial Centre,", ln=True, align='R')
                pdf.set_x(110)
                pdf.cell(90, 5, "87-105 Chatham Road, Tsim Sha Tsui, Kowloon.", ln=True, align='R')
                pdf.set_x(110)
                pdf.cell(90, 5, "Email: info@fhi.com.hk | Tel: +852 5622 2792", ln=True, align='R')
                pdf.ln(18)
                
                # 3. Title
                pdf.set_font("Arial", 'B', 22)
                pdf.cell(0, 15, "DEBIT NOTE", ln=True, align='C')
                pdf.ln(3)

                # 4. Policy Data Box
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, "  POLICY DETAILS", ln=True, fill=True)
                pdf.set_font("Arial", '', 10)
                
                for line in editable_details.split('\n'):
                    if line.strip():
                        pdf_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 6, f"  {pdf_line}") 
                
                pdf.ln(12) 

                # 5. Payment Methods
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
                
                # 6. Chop (Smaller 30mm) and Signature
                try:
                    pdf.image("chop.png", 155, 235, 30) 
                except:
                    pass
                
                pdf.set_xy(10, 260)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 5, f"Billing Date: {display_billing_date}", ln=False)

                pdf.set_xy(140, 270)
                pdf.set_font("Arial", 'I', 9)
                pdf.cell(60, 5, "Authorized Signature", align='C')

                # Filename and Download
                final_filename = f"{policy_no} {formatted_billing_date} DN.pdf"
                pdf_bytes = bytes(pdf.output())
                st.download_button(label=f"💾 Download: {final_filename}", data=pdf_bytes, file_name=final_filename, mime="application/pdf")

            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar.")
