import os
import json


def save_project(project_json):

    data = json.loads(project_json)
    
    if not data.get("files"):
        raise Exception(
            "LLM did not generate any files."
        )

    for file in data["files"]:
        file_path = os.path.join(
            "generated_projects/project",
            file["path"]
        )

        os.makedirs(
            os.path.dirname(file_path),
            exist_ok=True
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(file["content"])
