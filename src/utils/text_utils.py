import json
import logging
import re

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

"""Format trivia questions into a single message with options."""

def format_all_trivia(trivia_list):
    """Format 4 trivia questions + options as one HTML string message."""
    message = "<b> Trivia Time! Answer all 4 questions below:</b>\n\n"
    option_labels = ['A', 'B', 'C', 'D']

    for idx, trivia in enumerate(trivia_list, start=1):
        question = trivia.get("q")
        options = trivia.get("options", [])
        message += f"<b>{idx}. {question}</b>\n"
        for label, option_text in zip(option_labels, options):
            clean_option = re.sub(r"^\d+\.\s*", "", option_text)
            message += f"{label}. {clean_option}\n"
        message += "\n"

    message += (
        " Please reply to this message in this exact format:\n"
        "<code>1. A\n2. B\n3. C\n4. D</code>\n\n"
        "<b>You have 1 hour to submit your answers!</b>"
    )
    return message
