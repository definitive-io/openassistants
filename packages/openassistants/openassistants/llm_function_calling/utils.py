import json

import numpy as np
from openassistants.data_models.chat_messages import ensure_alternating


def chunk_list_by_max_size(lst, max_size):
    n = (len(lst) + max_size - 1) // max_size
    return [chunk.tolist() for chunk in np.array_split(lst, n)]


def find_json_substring(s):
    start = s.find("{")
    end = s.rfind("}") + 1
    if start != -1 and end != -1:
        return s[start:end]
    return None


async def generate_to_json(chat, messages) -> dict:
    response = await chat.ainvoke(ensure_alternating(messages))
    content = response.content

    json_substring = find_json_substring(content)
    if json_substring is not None:
        try:
            output_message = json.loads(json_substring)
            return output_message
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e, "\nResponse content:", content)
            return {}
    else:
        print("No JSON content found in response.")
        return {}
