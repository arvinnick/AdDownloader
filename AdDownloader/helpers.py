"""This module provides different helper functions for the AdDownloader."""

import json
import numpy as np
import requests
import pandas as pd
import os
from datetime import datetime
import openpyxl

def is_valid_date(date_string, date_format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
    

def is_valid_country(countries):
    country_codes = """ALL, BR, IN, GB, US, CA, AR, AU, AT, BE, CL, CN, CO, HR, DK, DO, EG, FI, FR, 
                DE, GR, HK, ID, IE, IL, IT, JP, JO, KW, LB, MY, MX, NL, NZ, NG, NO, PK, PA, PE, PH, 
                PL, RU, SA, RS, SG, ZA, KR, ES, SE, CH, TW, TH, TR, AE, VE, PT, LU, BG, CZ, SI, IS, 
                SK, LT, TT, BD, LK, KE, HU, MA, CY, JM, EC, RO, BO, GT, CR, QA, SV, HN, NI, PY, UY, 
                PR, BA, PS, TN, BH, VN, GH, MU, UA, MT, BS, MV, OM, MK, LV, EE, IQ, DZ, AL, NP, MO, 
                ME, SN, GE, BN, UG, GP, BB, AZ, TZ, LY, MQ, CM, BW, ET, KZ, NA, MG, NC, MD, FJ, BY, 
                JE, GU, YE, ZM, IM, HT, KH, AW, PF, AF, BM, GY, AM, MW, AG, RW, GG, GM, FO, LC, KY, 
                BJ, AD, GD, VI, BZ, VC, MN, MZ, ML, AO, GF, UZ, DJ, BF, MC, TG, GL, GA, GI, CD, KG, 
                PG, BT, KN, SZ, LS, LA, LI, MP, SR, SC, VG, TC, DM, MR, AX, SM, SL, NE, CG, AI, YT, 
                CV, GN, TM, BI, TJ, VU, SB, ER, WS, AS, FK, GQ, TO, KM, PW, FM, CF, SO, MH, VA, TD, 
                KI, ST, TV, NR, RE, LR, ZW, CI, MM, AN, AQ, BQ, BV, IO, CX, CC, CK, CW, TF, GW, HM, 
                XK, MS, NU, NF, PN, BL, SH, MF, PM, SX, GS, SS, SJ, TL, TK, UM, WF, EH"""
    country_codes = [code.strip() for code in country_codes.split(",")]
    if not isinstance(countries, list):
        countries = [countries]
    valid_countries = [code for code in countries if code in country_codes]
    
    return valid_countries

def is_valid_excel_file(file):
    # check if the path exists and has an Excel file extension
    path = os.path.join("data", file)
    if not os.path.exists(path) or not path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
        print(f"Excel file not found.")
        return False
    # try to read the excel file
    try:
        pd.read_excel(path)
        return True
    except Exception as e:  # catches any exception when trying to read
        print(f"Unable to read excel file: {e}.")
        return False



"""

########## JSON DATA PROCESSING
def load_json(file_path):
    # open the JSON file and read the content as text
    with open(file_path, 'r') as json_file:
        json_data = json_file.read()
    
    # parse and extract the data
    parsed_data = json.loads(json_data)
    data_list = parsed_data.get('data', [])
    len(data_list)
    df = pd.DataFrame(data_list)
    return df


def load_json_from_folder(folder_path):
    # Get a list of all files in the specified folder
    all_files = os.listdir(folder_path)
    
    # Filter only files with a JSON extension
    json_files = [file for file in all_files if file.endswith('.json')]
    dfs = []
    # Loop through each JSON file
    for json_file in json_files:
        # Construct the full file path
        file_path = os.path.join(folder_path, json_file)

        # Open the JSON file and read the content as text
        with open(file_path, 'r') as file:
            json_data = file.read()

        # Parse and extract the data
        parsed_data = json.loads(json_data)
        data_list = parsed_data.get('data', [])

        # Create a DataFrame from the current JSON data
        df = pd.DataFrame(data_list)

        # Append the DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    result_df = pd.concat(dfs, ignore_index=True)
    return result_df


# function that flattens the age_country_gender_reach_breakdown column 
def flatten_age_country_gender(row):
    flattened_data = []

    # Check if the row is empty and remove it
    if isinstance(row, float) and pd.isna(row):
        return flattened_data
    
    for entry in row:
        country = entry.get('country') # get the country to keep only BE or NL
        if country in ['BE', 'NL']: # maybe also adjust to take only the target country
            age_gender_data = entry.get('age_gender_breakdowns', [])
            for age_gender_entry in age_gender_data:
                # exclude entries with 'Unknown' age range
                if age_gender_entry.get('age_range', '').lower() != 'unknown':
                    # extract each field and flatten it together
                    flattened_entry = {
                        'country': country,
                        'age_range': age_gender_entry.get('age_range', ''),
                        'male': age_gender_entry.get('male', 0),
                        'female': age_gender_entry.get('female', 0),
                        'unknown': age_gender_entry.get('unknown', 0)
                    }
                    flattened_data.append(flattened_entry)
    return flattened_data

# indiv - procss only one file or entire folder
def transform_data(folder_path, indiv = False):
    if indiv:
        df = load_json(folder_path)
    else:
        df = load_json_from_folder(folder_path)

    # flatten the age_country_gender_breakdown for each ad
    df['flattened_data'] = df['age_country_gender_reach_breakdown'].apply(flatten_age_country_gender)
    # create a new DataFrame from the flattened data
    flattened_df = pd.DataFrame(df['flattened_data'].sum()) 

    # create a list of ids for the flattened data
    id_list = []
    for index, row in df.iterrows():
        id_list.extend([row['id']] * len(row['flattened_data']))
    flattened_df['id'] = id_list

    # convert to wide format
    wide_df = flattened_df.pivot_table(index=['id'], columns='age_range', values=['male', 'female', 'unknown'], aggfunc='first')
    # change the column names and reset the index
    wide_df.columns = ['_'.join(col) for col in wide_df.columns.values]
    wide_df.reset_index(inplace=True)

    # keep only the relevant columns and save data to csv
    final_data = df.iloc[:, :14].merge(wide_df, on="id")
    # better use column names
    return final_data

"""