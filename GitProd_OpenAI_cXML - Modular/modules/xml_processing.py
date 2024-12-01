# modules/xml_processing.py

import json
import xml.etree.ElementTree as ET
import streamlit as st
from modules.file_upload import sanitize_json_string  # Import the sanitize function

def recursive_parse_xml(element):
    parsed_dict = {}
    if element.attrib:
        parsed_dict['@attributes'] = element.attrib
    if element.text and element.text.strip():
        parsed_dict['#text'] = element.text.strip()
    for child in element:
        child_parsed = recursive_parse_xml(child)
        if child.tag in parsed_dict:
            if isinstance(parsed_dict[child.tag], list):
                parsed_dict[child.tag].append(child_parsed)
            else:
                parsed_dict[child.tag] = [parsed_dict[child.tag], child_parsed]
        else:
            parsed_dict[child.tag] = child_parsed
    return parsed_dict

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# Updated parse_cxml function to accept two arguments
def parse_cxml(file, sanitize_func):
    try:
        # Read the file content
        file_content = file.read().decode('utf-8')

        # Sanitize the JSON string to remove invalid control characters
        sanitized_content = sanitize_func(file_content)

        # Parse the sanitized JSON content
        json_data = json.loads(sanitized_content)

        # Create a dictionary to store the parsed data
        parsed_data = {}

        # First, extract the outer JSON fields (e.g., messageId, timestamp, etc.)
        parsed_data['messageId'] = json_data.get('messageId', None)
        parsed_data['timestamp'] = json_data.get('timestamp', None)
        parsed_data['eventType'] = json_data.get('eventType', None)
        parsed_data['correlationId'] = json_data.get('correlationId', None)
        parsed_data['clientId'] = json_data.get('clientId', None)
        parsed_data['version'] = json_data.get('version', None)
        parsed_data['supplierId'] = json_data.get('supplierId', None)
        parsed_data['buyerId'] = json_data.get('buyerId', None)
        parsed_data['origin'] = json_data.get('origin', None)

        # Extract the fields from the payload
        payload_data = json_data.get('payload', {})
        parsed_data['transactionId'] = payload_data.get('transactionId', None)
        parsed_data['documentNumber'] = payload_data.get('documentNumber', None)
        parsed_data['documentType'] = payload_data.get('documentType', None)
        parsed_data['s3Bucket'] = payload_data.get('s3Bucket', None)
        parsed_data['s3Key'] = payload_data.get('s3Key', None)

        # Extract and parse the attachments field from the payload
        attachments = payload_data.get('attachments', [])
        parsed_data['attachments'] = [{"Id": attachment.get('Id', None), "Url": attachment.get('Url', None)} for attachment in attachments]

        # Extract the cXML field from the payload
        cxml_string = payload_data.get('cxml', None)

        if cxml_string:
            # Parse the cXML string using xml.etree.ElementTree
            root = ET.fromstring(cxml_string)

            # Recursively parse the XML structure and add it to the parsed data
            parsed_data['cXML'] = recursive_parse_xml(root)

        else:
            st.error("No 'cxml' field found in the JSON payload.")
            return None

        return parsed_data

    except ET.ParseError as e:
        st.error(f"Error parsing cXML: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
