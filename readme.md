# BizCardX - Business Card Information Extractor

BizCardX is a Streamlit web application that empowers users to effortlessly extract essential details from business card images. The application utilizes the powerful easyOCR library for text extraction and PostgreSQL for data storage.

## Features

- **Upload Business Card Images:** Simply upload business card images in common formats such as JPG, JPEG, and PNG.

- **Extract Information:** Utilize easyOCR to process uploaded images and extract key information such as company name, cardholder name, designation, contact details, and address.

- **Database Integration:** Save the extracted information into a PostgreSQL database for seamless data management.

- **Retrieve and Edit Data:** View existing data in a user-friendly table, edit entries, and delete unwanted information.

## How to Use

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/BizCardX.git
   cd BizCardX
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
3. **Create secrets.toml file inside .streamlit folder**
    Create a directory .streamlit and create a file to save secrets secrets.toml
3. **Run the Application**
   ```bash
   streamlit run ocr_ui.py