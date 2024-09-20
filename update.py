import os
import hashlib
import json
import sys
import subprocess
import requests
from tqdm import tqdm

BASE_URL = "https://cdn.eastmile.org/eastmile-updates/client/"
JSON_URL = "https://cdn.eastmile.org/eastmile-updates/client_files.json"
DOWNLOAD_DIR = "./"

def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                sha1.update(data)
    except FileNotFoundError:
        return None
    return sha1.hexdigest()

def get_file_length(file_path):
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return None

def download_file(file_path, file_url):
    download_path = os.path.join(DOWNLOAD_DIR, file_path)

    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(download_path), exist_ok=True)

        total_size = int(response.headers.get('content-length', 0))
        with open(download_path, 'wb') as file, tqdm(
            desc=file_path,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            file=sys.stdout,
            dynamic_ncols=True,
        ) as bar:
            for data in response.iter_content(chunk_size=8192):
                file.write(data)
                bar.update(len(data))

        print(f"\rDescargado: {file_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"\rError al descargar {file_path}: {e}")

def get_file_info_from_json(json_url):
    try:
        response = requests.get(json_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el JSON: {e}")
        return None

def main():
    files_info = get_file_info_from_json(JSON_URL)
    
    if files_info is None:
        print("No se pudo obtener la información de los archivos.")
        return
    
    for file_info in files_info:
        file_path = file_info["Path"].replace("\\", "/")
        expected_sha1 = file_info["Hash"]
        expected_length = file_info["Length"]

        local_file_path = os.path.join(DOWNLOAD_DIR, file_path)

        local_sha1 = calculate_sha1(local_file_path)
        local_length = get_file_length(local_file_path)

        if local_sha1 != expected_sha1 or local_length != expected_length:
            file_url = BASE_URL + file_path
            download_file(file_path, file_url)
        else:
            print(f"\rArchivo actualizado: {file_path}")
    if os.name == "nt":
	    subprocess.run(["NostaleClientX.exe", "EntwellNostaleClient", "0"])
    else:
	    subprocess.run(["wine", "NostaleClientX.exe", "EntwellNostaleClient", "0"])
if __name__ == "__main__":
    main()

