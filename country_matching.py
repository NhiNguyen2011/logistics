import sys
import pandas as pd
import numpy as np
import os
import re
import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key  = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def required_countries(file_path):
    länder_dict = {}
    gruppe_dict = {}

    # Open and read the text file   
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Process the lines to create the dictionary
    for line in lines:
        parts = line.strip().split(' - ')  
        key = int(parts[0])  # integer as key (wirtschaftsregion)
        values = [parts[1]]   # words as values (Länder)
        
        if len(parts) > 2:
            group = parts[1]
            members = parts[2:]
            gruppe_dict[group] = members   
        
        # Check if the key already exists in the dictionary
        if key in länder_dict:
            # If the key exists, append the new values to the existing list of values
            länder_dict[key].extend(values)
        else:
            # If the key is new, create a new entry in the dictionary
            länder_dict[key] = values
    
    return länder_dict, gruppe_dict

def process_input_text(input_file, gruppe_dict):
    with open(input_file,'r', encoding="utf-8") as file:
        content = file.read()
        
    pattern = re.compile(r'\b([A-Z]{2,4})\b')

    match = re.findall(pattern,content)

    if len(match) >= 10: 
        pattern1 = re.compile("Cariforum", re.IGNORECASE)
        content = pattern1.sub("CAF", content)

        input_countries = re.findall(pattern,content)
    else: 
        text = content
        prompt = f"""
        Given a text containing country names and specific regional groupings or partnerships in various languages, 
        transform the country names into corresponding ISO 3166-1 alpha-2 country codes and 
        specific regional groupings or partnerships into corresponding abbreviations based on the following instructions:          
            - Overseas Countries and Territories: OCT
            - Eastern and Southern Africa: ESA
            - Cariforum: CAF
            - Southern African Development Community: SADC
            - Western Pacific States: WPS
            - European Economic Area: EEA
            - Central America: CAM
            - Central Africa: CAS
            - Andean countries: AND
        Provide them in a list format
        
        ```{text}```
        """
        input_countries = get_completion(prompt)

    for key, values in gruppe_dict.items():
        if (key in input_countries) and any(value in input_countries for value in values):
            input_countries.remove(key)
    
    return input_countries

def matching_countries(länder_dict, gruppe_dict, input_countries):
    log = []

    for economic_area, countries in länder_dict.items():
        missing_countries = []
        for country in countries:
            match2 = re.compile(r'(\w+)\s*\/\s*(\w+)', flags=re.IGNORECASE).search(country)
            if match2:
                if (match2.group(1) not in input_countries) and (match2.group(2) not in input_countries):
                    missing_countries.append(country)
                continue
            if country not in input_countries:
                missing_countries.append(country)

        for missing in missing_countries:
            if missing in gruppe_dict.keys():
                missing_member = []
                for member in gruppe_dict[missing]:
                    match1 = re.compile(r'\(\s*(\w+)\s*\)').search(member)
                    if match1:
                        member = match1.group(1)
                    if member not in input_countries:
                        missing_member.append(member)
                if not missing_member:
                    missing_countries = [x for x in missing_countries if x != missing]
                elif len(missing_member) != len(gruppe_dict[missing]):
                    text = f"Gruppe {missing} ist unvollständig, fehlende Länder: {missing_member}"
                    if member == "HT" or member == "ZM":
                        text = text + f" aber {member} noch nicht anwendbar"
                    log.append(text)  
            
        if missing_countries:
            log.append(f"Die Wirtschaftsgebiet {economic_area} ist unvollständig. Fehlende Länder: {missing_countries}")

    if not log:
        log.append("Alles in Ordnung")

    for item in log:
        print(item)                   


def main():
    länder_dict, gruppe_dict = required_countries(file_path)
    input_countries = process_input_text(input_file, gruppe_dict)
    matching_countries(länder_dict, gruppe_dict, input_countries)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]
    file_path = 'Ländervorgaben.txt' 
    main()



