import json
import re


def extract_json(text):

    text = re.sub(
        r"```json|```",
        "",
        text
    ).strip()

    match = re.search(
        r'\{.*\}',
        text,
        re.DOTALL
    )

    if match:
        return json.loads(
            match.group()
        )

    return None
