import re
import json
import logging
from prettytable import PrettyTable


def format_json_str_to_json(json_str: str):
    
  """Format JSON string to JSON Object"""
  try:
    json_str = re.sub(r'^```json|```', '', json_str.strip(), flags=re.MULTILINE)
    
    json_object = json.loads(json_str)

    return json_object
  except Exception as e:
      logging.error(f"Unable to parse JSON: {e}")
      return []
  

def format_json_to_table(json_data: list[dict]) -> str:
    try:
        data = json_data

        full_headers = []
        full_values = []
        for item in data:
            headers = []
            values = []
            for key in item.keys():
                header = key
                if isinstance(item[key], dict):
                    for key_2 in item[key]:
                        header += "/" + key_2
                        value = item[key][key_2]
                        headers.append(value)
                        values.append(value)

                else:
                    value = item[key]
                    headers.append(header)
                    values.append(value)
            full_headers.append(headers)
            full_values.append(values)

        table = PrettyTable()

        table.field_names = full_headers[0]
        table.add_rows(full_values)

        table.align = "l"
        table.max_width = 12

        stringify_table = table.get_string()

        return stringify_table

    except Exception as e:
        logging.error(
            f"Failed to convert JSON to table format. Details: {e}"
        )
