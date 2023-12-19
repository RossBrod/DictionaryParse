import json
import uuid
import string
import re

from bs4 import BeautifulSoup, NavigableString

def safe_get_text(element):
    return element.get_text().strip() if element else ''

def extract_definition(sibling):
    definition = ''
    while sibling:
        if isinstance(sibling, NavigableString):
            definition += sibling.strip()
        elif sibling.name in ['i', 'em', 'b', 'a']:  # Include tags like <i>, <em>, <b>, <a>
            if sibling.name == 'b' and re.match(r'^[a-zA-Z0-9]+\b', sibling.get_text().strip()):
                # Skip markers like "1:", "a:"
                pass
            else:
                definition += ' ' + sibling.get_text().strip() + ' '
        else:
            break
        sibling = sibling.next_sibling
    return definition.strip()

def parse_sub_definitions(dd_element):
    sub_definitions = []
    sub_items = []
    for element in dd_element.children:
        if element.name == 'b':
            marker_text = safe_get_text(element)
            # Check if this is a main definition (e.g., "1:")
            if re.match(r'^\d+\b', marker_text):
                if sub_items:
                    sub_definitions.append(sub_items)
                    sub_items = []
                definition_text = extract_definition(element)
                sub_definitions.append({"definition": definition_text})
            # Check if this is a sub-definition (e.g., "a:")
            elif re.match(r'^[a-zA-Z]+\b', marker_text):
                definition_text = extract_definition(element)
                sub_items.append({"definition": definition_text})
    if sub_items:
        sub_definitions.append(sub_items)
    return sub_definitions

def ProcessDictionary(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    main_term = safe_get_text(soup.find('h1'))
    main_definition_element = soup.find('dl').find('dd')
    sub_definitions = parse_sub_definitions(main_definition_element)

    # final_definition =  safe_get_text(main_definition_element.contents[0])
    # final_definition =final_definition.lstrip(": ")
    # print("DEBUG123:"+ final_definition )

    json_data = {
        "term": main_term,
        "definition": safe_get_text(main_definition_element.contents[0]),
        "sub_definitions": sub_definitions
    }
    return json.dumps(json_data, indent=4)

# def clean_definitions(data):
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if key == "definition" and isinstance(value, str) and value.startswith(": "):
#                 data[key] = value[2:]
#             else:
#                 clean_definitions(value)
#     elif isinstance(data, list):
#         for item in data:
#             clean_definitions(item)
#     return data

def misc_cleaner(json_string):
    try:
        data = json.loads(json_string)  # Parse the JSON string into a Python object

        def clean_definitions(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "definition" and isinstance(value, str) and value.startswith(": "):
                        data[key] = value[2:]
                    else:
                        clean_definitions(value)
            elif isinstance(data, list):
                for item in data:
                    clean_definitions(item)

        clean_definitions(data)
        return json.dumps(data, indent=4)  # Convert the modified object back to a JSON string

    except json.JSONDecodeError as e:
        return f"JSON decoding error: {e}"

with open("bot55-d4c16-default-rtdb-export.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Flatten the structure and clean HTML, add IDs, and add linkedTermIDs

all_elements = []
for letter, elements in data['DATA'].items():
    for item in elements:
         #if item["title"] == "Abandonment":
            # test123=clean_definitions(convert_html_to_json( item['body']))
            # cleaned_json_str = json.dumps(test123, indent=4)
            # print(cleaned_json_str)
            #t0=ProcessDictionary(item['body'])
            # print("Type of data:", type(t0)) 
            # print(t0)

            # t1=convert_html_to_json(json.dumps(item['body'],indent=4))
            # t2 = json.loads(t1)
            # your_data_str = convert_html_to_json(json.dumps(item['body'],indent=4))
            #c1=misc_cleaner(ProcessDictionary(item['body']))
            #cjs = json.dumps(c1, indent=4)
            #print(c1)
        all_elements.append(json.loads(misc_cleaner(ProcessDictionary(item['body']))))
             # Convert the JSON string to a Python dictionary
    #all_elements.append(json.loads(json_output))

# try:
#     # Convert the JSON string to a Python object
#     your_data = json.loads(your_data_str)
#     #print("Parsed Data:", your_data)  # Debugging statement

#     # Clean the definitions
#     cleaned_data = clean_definitions(your_data)

#     # Convert back to JSON string for display
#     cleaned_json_str = json.dumps(cleaned_data, indent=4)
#     #print(cleaned_json_str)
# except json.JSONDecodeError as e:
#     print("JSON decoding error:", e)             

    #all_elements.append(json.loads(json_output))
        
#Save the modified JSON data
with open('modified_json_file5.json', 'w') as file:
    json.dump(all_elements, file, indent=4)