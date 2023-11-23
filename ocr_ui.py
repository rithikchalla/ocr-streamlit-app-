import streamlit as st
import ocr_api
import easyocr
import io
from PIL import Image


# Page functions
def home_page():
    st.header("Business Card Information Extractor")
    st.write("""Welcome to the Business Card Information Extractor app! 
             This Streamlit application empowers users to effortlessly extract 
             essential details from uploaded business card images using the 
             powerful easyOCR library. The extracted information includes key 
             elements such as the company name, cardholder name, designation, 
             mobile number, email address, website URL, area, city, state, and pin code.
             """)
    st.markdown("""
        <h3>How It Works</h3>
        <ol>
                <li><b>Upload Your Business Card Image:</b> Simply use the file uploader 
                in the sidebar to select and upload the image of the business 
                card you'd like to extract information from.</li>
                <li><b>Extracted Information Display:</b> Once the image is uploaded, the 
                application utilizes easyOCR to process the image and extract relevant 
                details. The extracted information is then presented in a clean and 
                organized manner in the application's graphical user interface (GUI).</li>
                <li><b>Database Integration:</b>The application goes a step further by 
                allowing users to save the extracted information into a database. 
                The database, powered by PostgreSQL, stores multiple entries, 
                each associated with its respective business card image and extracted 
                information.</li>
                <li><b>Database Operations:</b>Users have the flexibility to interact 
                with the stored data through the Streamlit UI. You can read the data, 
                update existing entries, and delete entries effortlessly, providing a 
                seamless experience.</li>
        </ol>
        
    """,
    unsafe_allow_html=True)

def upload_data_page():
    st.header("Upload Images")
    uploaded_file = st.file_uploader("Choose a business card image", 
                                     type=["jpg", "jpeg", "png"])
    
    col1, col2 = st.columns(2)
    
    if uploaded_file is not None:
        col1.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        response = ocr_api.extract_information(uploaded_file.getvalue(), 
                                               st.session_state.ocr_reader_object)
        # Allow users to edit the extracted values
        col2.write("Edit Extracted Information:")
        edited_info = {}
        for key, value in response[1].items():
            edited_value = col2.text_input(f"Edit {key}:", ' '.join(value))
            edited_info[key] = edited_value

        # Option to update the extracted information
        if col2.button("Save Information to Database"):
            with st.spinner('Saving Information to database'):
                ocr_api.insert_into_database(edited_info, uploaded_file.read(), st.session_state.conn)
            col2.success("Information successfully saved to database")


def saved_info_page():
    st.header('Retrieve Existing Data')

    # Fetch data from the database
    data = ocr_api.fetch_data_from_database(st.session_state.conn)

    data_to_be_displayed = data.drop(columns=['image_data'])
    # Display the data in a table
    st.table(data_to_be_displayed)

    tab1, tab2 = st.tabs(['Update Data', 'Delete Data'])

    with tab1:
        # Option to edit or delete entries
        selected_entry_id = st.selectbox(
                    "Select the Id you want to update",
                   data['id'],
                    index=None,
                    placeholder="Select contact method...",
        )

        # Retrieve selected entry for editing
        if selected_entry_id:
            selected_entry = ocr_api.fetch_entry_by_id(selected_entry_id, st.session_state.conn)
            
            col1, col2 = st.columns(2)
            if selected_entry:
                col1.image(Image.open(io.BytesIO(selected_entry['image_data'])), caption="Uploaded Image", use_column_width=True)
                # Display entry for editing
                edited_info = {}
                for key, value in selected_entry.items():
                    if key != 'id' or key != 'image_data':
                        edited_value = col2.text_input(f"Edit {key}:", value)
                        edited_info[key] = edited_value

                # Option to update the edited information
                if st.button("Update Information"):
                    ocr_api.update_entry(selected_entry_id, edited_info, st.session_state.conn)
                    st.success("Information successfully updated")
                    st.rerun()

    with tab2:
        # Option to edit or delete entries
        selected_entry_id = st.selectbox(
                    "Select the Id you want to delete",
                   data['id'],
                    index=None,
                    placeholder="Select contact method...",
        )

        if selected_entry_id:
            with st.spinner("Deleting data from the database"):
                ocr_api.delete_entry(selected_entry_id, st.session_state.conn)
            st.success("Successfully Deleted!")
            st.rerun()

    

# Main function
def main():
    if 'ocr_reader_object' not in st.session_state:
        st.session_state.ocr_reader_object = easyocr.Reader(['en'])

    if 'conn' not in st.session_state:
        st.session_state.conn = ocr_api.connect_to_postgre(st.secrets['host'], 
                                                           st.secrets['port'],
                                                           st.secrets['database'],
                                                           st.secrets['user'],
                                                           st.secrets['password'])
        ocr_api.create_table(st.session_state.conn)

    st.title('BizCardX Extract text from Buisness cards')
    st.sidebar.title("Navigation Menu")

    # Create custom styled buttons
    selection = st.sidebar.selectbox(
        "Select an option from the below options",
        ("Home", "Upload Documents", "Retrieve Data")
    )

    # Add CSS to adjust the width of the sidebar
    st.markdown(
        """
        <style>
            .st-emotion-cache-vk3wp9 {
                width: 20% !important;
            }
            .stHeadingContainer {
                text-align: center;
            }
            .stButton {
                width: 100% !important; 
                padding: 0px; 
                color: Black; 
                text-align: center; 
                cursor: pointer;
                display: grid;
            }
            .st-emotion-cache-1y4p8pa {
                max-width: 100%;
                padding: 1rem 1rem 10rem;
            }
            .st-emotion-cache-1y4p8pa {
                max-width: 100%;
                font-size: 10px !important;
                padding: 1rem 1rem 10rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Determine which button is clicked and show the corresponding page
    if selection == 'Home':
        home_page()

    if selection == 'Upload Documents':
        upload_data_page()

    if selection == 'Retrieve Data':
        saved_info_page()

# Run the app
if __name__ == "__main__":
    main()
