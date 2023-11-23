import re
import psycopg2
import pandas as pd
from easyocr import Reader

def extract_information(image, ocr_reader: Reader):
    results = ocr_reader.readtext(image, detail = 0, paragraph=False)
    return (results, get_data(results))

def get_data(res):
    data = {
        "website": [],
        "email": [],
        "mobile_number": [],
        "company_name": [],
        "card_holder": [],
        "designation": [],
        "area": [],
        "city": [],
        "state": [],
        "pin_code": [],
    }

    for ind, i in enumerate(res):
        # To get WEBSITE_URL
        if "www." in i.lower():
            data["website"].append(i)
        elif "WWW" in i:
            data["website"] =  "www." + res[5]

        # To get EMAIL ID
        elif "@" in i:
            data["email"].append(i)

        # To get MOBILE NUMBER
        elif "-" in i:
            data["mobile_number"].append(i)
            if len(data["mobile_number"]) == 2:
                data["mobile_number"] = " & ".join(data["mobile_number"])

        # To get COMPANY NAME
        elif ind == len(res) - 1:
            data["company_name"].append(i)

        # To get CARD HOLDER NAME
        elif ind == 0:
            data["card_holder"].append(i)

        # To get DESIGNATION
        elif ind == 1:
            data["designation"].append(i)

        # To get AREA
        if re.findall("^[0-9].+, [a-zA-Z]+", i):
            data["area"].append(i.split(",")[0])
        elif re.findall("[0-9] [a-zA-Z]+", i):
            data["area"].append(i)

        # To get CITY NAME
        match1 = re.findall(".+St , ([a-zA-Z]+).+", i)
        match2 = re.findall(".+St,, ([a-zA-Z]+).+", i)
        match3 = re.findall("^[E].*", i)
        if match1:
            data["city"].append(match1[0])
        elif match2:
            data["city"].append(match2[0])
        elif match3:
            data["city"].append(match3[0])

        # To get STATE
        state_match = re.findall("[a-zA-Z]{9} +[0-9]", i)
        if state_match:
            data["state"].append(i[:9])
        elif re.findall("^[0-9].+, ([a-zA-Z]+);", i):
            data["state"].append(i.split()[-1])
        if len(data["state"]) == 2:
            data["state"].pop(0)

        # To get PINCODE
        if len(i) >= 6 and i.isdigit():
            data["pin_code"].append(i)
        elif re.findall("[a-zA-Z]{9} +[0-9]", i):
            data["pin_code"].append(i[10:])

    return data

def connect_to_postgre(host, port, database, user, password):
    """
        Connects to a PostgreSQL database running on GCP.
        Args:
            host: The host of the PostgreSQL database instance.
            port: The port of the PostgreSQL database instance.
            database: The name of the PostgreSQL database.
            username: The username to use to connect to the PostgreSQL database.
            password: The password to use to connect to the PostgreSQL database.
        Returns:
            A psycopg2 connection object.
    """

    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

def create_table(connection):
    cursor = connection.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS business_card_info (
            id SERIAL PRIMARY KEY,
            image_data BYTEA,
            company_name VARCHAR(255),
            name VARCHAR(255),
            designation VARCHAR(255),
            mobile_number VARCHAR(15),
            email_address VARCHAR(255),
            website_url VARCHAR(255),
            area VARCHAR(255),
            city VARCHAR(255),
            state VARCHAR(255),
            pin_code VARCHAR(10)
        );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()

def insert_into_database(info_dict, image_data, connection):
    cursor = connection.cursor()
    insert_query = """
        INSERT INTO business_card_info (
            image_data, company_name, name, designation,
            mobile_number, email_address, website_url,
            area, city, state, pin_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (
        image_data,
        info_dict['company_name'],
        info_dict['card_holder'],
        info_dict['designation'],
        info_dict['mobile_number'],
        info_dict['email'],
        info_dict['website'],
        info_dict['area'],
        info_dict['city'],
        info_dict['state'],
        info_dict['pin_code']
    ))
    connection.commit()
    cursor.close()

def fetch_data_from_database(connection):
    cursor = connection.cursor()
    fetch_query = """
        SELECT * FROM business_card_info;
    """
    cursor.execute(fetch_query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    return df

def fetch_entry_by_id(entry_id, connection):
    cursor = connection.cursor()
    fetch_query = """
        SELECT * FROM business_card_info WHERE id = %s;
    """
    cursor.execute(fetch_query, (entry_id,))
    entry = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    entry_dict = dict(zip(columns, entry)) if entry else {}
    cursor.close()
    return entry_dict

def update_entry(entry_id, info_dict, connection):
    cursor = connection.cursor()
    update_query = """
        UPDATE business_card_info
        SET 
            company_name = %s,
            name = %s,
            designation = %s,
            mobile_number = %s,
            email_address = %s,
            website_url = %s,
            area = %s,
            city = %s,
            state = %s,
            pin_code = %s
        WHERE id = %s;
    """
    cursor.execute(update_query, (
        info_dict['company_name'],
        info_dict['name'],
        info_dict['designation'],
        info_dict['mobile_number'],
        info_dict['email_address'],
        info_dict['website_url'],
        info_dict['area'],
        info_dict['city'],
        info_dict['state'],
        info_dict['pin_code'],
        entry_id
    ))
    connection.commit()
    cursor.close()

def delete_entry(entry_id, connection):
    cursor = connection.cursor()
    delete_query = """
        DELETE FROM business_card_info WHERE id = %s;
    """
    cursor.execute(delete_query, (entry_id,))
    connection.commit()
    cursor.close()