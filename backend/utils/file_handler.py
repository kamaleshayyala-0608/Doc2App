import os

UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "extracted_text"


def save_uploaded_file(uploaded_file):
    file_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def save_extracted_text(filename, text):
    os.makedirs(TEXT_FOLDER, exist_ok=True)
    txt_file = os.path.join(
        TEXT_FOLDER,
        filename + ".txt"
    )

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(text)
