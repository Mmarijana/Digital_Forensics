import os
import json
import zipfile


class FBArchiveLoader:
    """
    Loader radi:
    - ekstrakciju ZIP-a
    - pronalazak ključnih fajlova
    - učitavanje JSON-a
    """

    @staticmethod
    def extract_zip(zip_path, extract_dir):
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
        return extract_dir

    @staticmethod
    def load_json(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def find_account_activity(extract_dir):
        candidate = os.path.join(extract_dir, "account_activity.json")
        return candidate if os.path.exists(candidate) else None
