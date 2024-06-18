import sys
import requests

def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_filename, 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    download_url = sys.argv[1]
    local_filename = '/app/requirements.txt'
    download_file(download_url, local_filename)
