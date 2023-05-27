# Import needed dependencies
import asyncio
import requests
import sqlite3
import re
import os
from os import urandom
from tqdm import tqdm
import subprocess
import uuid
import glob
import zipfile
import shutil
import base64
import json
import argparse
import Licence_cURL

# Initialize argparse and set variable
parser = argparse.ArgumentParser(description="Options for manual download")
# Video argument
parser.add_argument('-v', '--video-res', help="Desired video resolution (by width)", metavar="", default=None)
# Audio argument
parser.add_argument('-alang', '--audio-lang', help="Desired audio language", metavar="", default=None)
# Subtitle argument
parser.add_argument('-slang', '--subtitle-lang', help="Desired subtitle language", metavar="", default=None)
# Assign the args a variable
args = parser.parse_args()

# Get current working directory
main_directory = os.getcwd()

# Get directories in the current working directory
directories_in_current_working_directory = os.listdir(fr'{main_directory}')

# Set required directories
required_directories = ['binaries', 'temp', 'downloads', 'keys']

# Create directories in current working directory if they do not exist
for directory in required_directories:
    if directory not in directories_in_current_working_directory:
        os.makedirs(f'{main_directory}\\{directory}')

# Create database and table for local key caching if they don't exist
dbconnection = sqlite3.connect(f"{main_directory}\\keys\\database.db")
dbcursor = dbconnection.cursor()
dbcursor.execute('CREATE TABLE IF NOT EXISTS "DATABASE" ( "pssh" TEXT, "keys" TEXT, PRIMARY KEY("pssh") )')
dbconnection.close()

# Assigning and checking all required external binaries exist
required_binaries = ["n_m3u8dl-re.exe", "mp4decrypt.exe", "ffmpeg.exe"]

# Check if the required binaries exist, if not, download them.
for binary in required_binaries:
    if not os.path.isfile(f"{main_directory}\\binaries\\{binary}"):
        save_path = f"{main_directory}\\temp"
        if binary == "ffmpeg.exe":
            ffmpeg_download = requests.get("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", stream=True)
            total_size = int(ffmpeg_download.headers.get('content-length', 0))
            with open(f"{save_path}\\ffmpeg.zip", 'wb') as download:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading ffmpeg.zip") as progress_bar:
                    for data in ffmpeg_download.iter_content(chunk_size=1024):
                        download.write(data)
                        progress_bar.update(len(data))
            with zipfile.ZipFile(f"{main_directory}\\temp\\ffmpeg.zip", "r") as ffmpeg_zip:
                file_count = len(ffmpeg_zip.infolist())
                with tqdm(total=file_count, unit='file', desc="Extracting ffmpeg.zip") as unzip_progress_bar:
                    for file in ffmpeg_zip.infolist():
                        ffmpeg_zip.extract(file, path=f"{main_directory}\\temp")
                        unzip_progress_bar.update(1)
            shutil.copy2(f"{main_directory}\\temp\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe", f"{main_directory}\\binaries")
            os.remove(f"{main_directory}\\temp\\ffmpeg.zip")
            shutil.rmtree(f"{main_directory}\\temp\\ffmpeg-master-latest-win64-gpl")
            print()
        elif binary == "mp4decrypt.exe":
            mp4decrypt_download = requests.get("https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-639.x86_64-microsoft-win32.zip", stream=True)
            total_size = int(mp4decrypt_download.headers.get('content-length', 0))
            with open(f"{save_path}\\mp4decrypt.zip", 'wb') as download:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading mp4decrypt.zip") as progress_bar:
                    for data in mp4decrypt_download.iter_content(chunk_size=1024):
                        download.write(data)
                        progress_bar.update(len(data))
            with zipfile.ZipFile(f"{main_directory}\\temp\\mp4decrypt.zip", "r") as mp4decrypt_zip:
                file_count = len(mp4decrypt_zip.infolist())
                with tqdm(total=file_count, unit='file', desc="Extracting mp4decrypt.zip") as unzip_progress_bar:
                    for file in mp4decrypt_zip.infolist():
                        mp4decrypt_zip.extract(file, path=f"{main_directory}/temp")
                        unzip_progress_bar.update(1)
            shutil.copy2(f"{main_directory}\\temp\\Bento4-SDK-1-6-0-639.x86_64-microsoft-win32\\bin\\mp4decrypt.exe", f"{main_directory}\\binaries")
            os.remove(f"{main_directory}\\temp\\mp4decrypt.zip")
            shutil.rmtree(f"{main_directory}\\temp\\Bento4-SDK-1-6-0-639.x86_64-microsoft-win32")
            print()
        elif binary == "n_m3u8dl-re.exe":
            n_m3u8dl_re_download = requests.get("https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.1.6-beta/N_m3u8DL-RE_Beta_win-x64_20230412.zip", stream=True)
            total_size = int(n_m3u8dl_re_download.headers.get('content-length', 0))
            with open(f"{save_path}\\n_m3u8dl-re.zip", 'wb') as download:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading n_m3u8dl-re.zip") as progress_bar:
                    for data in n_m3u8dl_re_download.iter_content(chunk_size=1024):
                        download.write(data)
                        progress_bar.update(len(data))
            with zipfile.ZipFile(f"{main_directory}\\temp\\n_m3u8dl-re.zip", "r") as nm3u8dl_re_zip:
                file_count = len(nm3u8dl_re_zip.infolist())
                with tqdm(total=file_count, unit='file', desc="Extracting n_m3u8dl-re.zip") as unzip_progress_bar:
                    for file in nm3u8dl_re_zip.infolist():
                        nm3u8dl_re_zip.extract(file, path=f"{main_directory}\\temp")
                        unzip_progress_bar.update(1)
            shutil.copy2(f"{main_directory}\\temp\\N_m3u8DL-RE_Beta_win-x64\\N_m3u8DL-RE.exe", f"{main_directory}/binaries")
            os.remove(f"{main_directory}\\temp\\n_m3u8dl-re.zip")
            shutil.rmtree(f"{main_directory}\\temp\\N_m3u8DL-RE_Beta_win-x64")
            print()

# Assign binaries a variable
n_m3u8dl_re = f'{main_directory}\\binaries\\{required_binaries[0]}'
mp4decrypt = f'{main_directory}\\binaries\\{required_binaries[1]}'
ffmpeg = f'{main_directory}\\binaries\\{required_binaries[2]}'

# Check if API key exists, if not create file and ask for key
if not os.path.isfile(f"{main_directory}\\api-key.txt"):
    with open(f'{main_directory}\\api-key.txt', 'w') as api_key_text:
        api_key = input(f"\nIf you have an API key please input it now: ")
        api_key_text.write(api_key)

# Get API key if file already exists
with open(f'{main_directory}\\api-key.txt') as api_key:
    api_key = api_key.readline()

# Print out API key
print(f"\nYour API key: {api_key}")


# Define MPD / m3u8 PSSH parser
async def manifest_pssh_parse(manifest_url):
    manifest = manifest_url
    try:
        response = requests.get(manifest)
    except:
        pssh = input("Couldn't retrieve manifest, please input PSSH: ")
        return pssh
    try:
        matches = re.finditer(r'<cenc:pssh(?P<any>(.*))>(?P<pssh>(.*))</cenc:pssh>', response.text)
        pssh_list = []

        for match in matches:
            if match.group and not match.group("pssh") in pssh_list and len(match.group("pssh")) < 300:
                pssh_list.append(match.group("pssh"))

        if len(pssh_list) < 1:
            matches = re.finditer(r'URI="data:text/plain;base64,(?P<pssh>(.*))"', response.text)
            for match in matches:
                if match.group("pssh") and match.group("pssh").upper().startswith("A") and len(match.group("pssh")) < 300:
                    pssh_list.append(match.group("pssh"))
        return f'{pssh_list[0]}'
    except:
        pssh = input("Couldn't find PSSH in manifest, please input PSSH")
        return pssh


# Define key cache function
async def key_cache(pssh: str, db_keys: str):
    dbconnection = sqlite3.connect(f"{main_directory}\\keys\\database.db")
    dbcursor = dbconnection.cursor()
    dbcursor.execute("INSERT or REPLACE INTO database VALUES (?, ?)", (pssh, db_keys))
    dbconnection.commit()
    dbconnection.close()


# Define retrieve keys remotely function
async def retrieve_keys_remotely(pssh: str = None, license_url: str = None):
    # Set the API URL to a pywidevine served API
    api_url = "https://api.cdrm-project.com"

    # Set the API device you want to use for decryption
    api_device = "CDM"

    # Get the PSSH
    pssh = pssh

    # Get the license URL
    license_url = license_url

    # Set your API key to be sent with headers
    x_headers = {
        "X-Secret-Key": api_key
    }

    # Open a session on your API device via your API key sent in headers
    open_session = requests.get(url=f"{api_url}/{api_device}/open", headers=x_headers)

    # Get the session ID
    session_id = open_session.json()["data"]["session_id"]

    # Set JSON data to send to create the license challenge
    license_challenge_json_data = {
        "session_id": session_id,
        "init_data": pssh
    }

    # Create the license challenge
    licence_challenge = requests.post(url=f"{api_url}/{api_device}/get_license_challenge/AUTOMATIC", headers=x_headers,
                                      json=license_challenge_json_data)

    # Retrieve the license message
    license_message = licence_challenge.json()["data"]["challenge_b64"]

    # Send the license challenge
    license = requests.post(
        headers=Licence_cURL.headers,
        url=license_url,
        data=base64.b64decode(license_message)
    )

    # Set JSON data to parse the license
    parse_license_json_data = {
        "session_id": session_id,
        "license_message": f"{base64.b64encode(license.content).decode()}"
    }

    # Send the request to parse the license
    requests.post(f"{api_url}/{api_device}/parse_license", json=parse_license_json_data, headers=x_headers)

    # Retrieve the keys from the parsed license
    get_keys = requests.post(f"{api_url}/{api_device}/get_keys/ALL", json={"session_id": session_id}, headers=x_headers)

    # Set DB keys
    db_keys = ''

    # Set mp4decrypt keys
    mp4decrypt_keys = []

    # Iterate through key response, if signing key, ignore
    for key in get_keys.json()["data"]["keys"]:
        if not key["type"] == "SIGNING":
            db_keys += f"{key['key_id']}:{key['key']}\n"
            mp4decrypt_keys.append('--key')
            mp4decrypt_keys.append(f"{key['key_id']}:{key['key']}\n")
            await key_cache(pssh=pssh, db_keys=db_keys)

    # Close the session
    requests.get(f"{api_url}/{api_device}/close/{session_id}", headers=x_headers)

    # Return keys if function is called from variable assignment
    return db_keys, mp4decrypt_keys


# Define retrieve keys remotely VDOCipher function
async def retrieve_keys_remotely_vdocipher(mpd: str = None):
    # Get URL from function
    url = input(f"Video URL: ")

    # Set the VDOCipher token headers
    token_headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        # Comment this line out if using for anything other than https://www.vdocipher.com/blog/2014/12/add-text-to-videos-with-watermark/
        'Origin': f"https://{urandom(8).hex()}.com",
    }

    # Set the token response
    token_response = requests.get(url, cookies=Licence_cURL.cookies, headers=token_headers)
    try:
        otp_match = re.findall(r"otp: '(.*)',", token_response.text)[0]
        playbackinfo_match = re.findall(r"playbackInfo: '(.*)',", token_response.text)[0]
    except IndexError:
        try:
            otp_match = re.findall(r"otp=(.*)&", token_response.text)[0]
            playbackinfo_match = re.findall(r"playbackInfo=(.*)", token_response.text)[0]
        except IndexError:
            print("\nAn error occurred while getting otp/playback")
            exit()

    # Set the video ID
    video_id = json.loads(base64.b64decode(playbackinfo_match).decode())["videoId"]

    # Set new token response (1)
    token_response = requests.get(f'https://dev.vdocipher.com/api/meta/{video_id}', headers=token_headers)
    try:
        license_url = token_response.json()["dash"]["licenseServers"]["com.widevine.alpha"].rsplit(":", 1)[0]
        mpd = token_response.json()["dash"]["manifest"]
    except KeyError:
        print("\n An error occurred while getting mpd/license url")

    # Set new token response (2)
    token_response = requests.get(mpd, headers=token_headers)

    # Set API URL
    api_url = "https://api.cdrm-project.com"

    # Set API Device
    api_device = "CDM"

    # Retrieve PSSH
    pssh = re.search(r"<cenc:pssh>(.*)</cenc:pssh>", token_response.text).group(1)

    # Set API headers
    x_headers = {
        "X-Secret-Key": api_key
    }

    # Open API session
    open_session = requests.get(url=f"{api_url}/{api_device}/open", headers=x_headers)

    # Set the session ID
    session_id = open_session.json()["data"]["session_id"]

    # Send json data to get license challenge
    license_challenge_json_data = {
        "session_id": session_id,
        "init_data": pssh
    }

    # Get the license challenge from PSSH
    licence_challenge = requests.post(url=f"{api_url}/{api_device}/get_license_challenge/AUTOMATIC", headers=x_headers,
                                      json=license_challenge_json_data)

    # Set the final token
    token = {
        "otp": otp_match,
        "playbackInfo": playbackinfo_match,
        "href": url,
        "tech": "wv",
        "licenseRequest": licence_challenge.json()["data"]["challenge_b64"]
    }

    # Send challenge
    license = requests.post(
        url=license_url,
        json={'token': f'{base64.b64encode(json.dumps(token).encode("utf-8")).decode()}'}
    )

    # Set the parsing JSON data
    parse_license_json_data = {
        "session_id": session_id,
        "license_message": license.json()["license"]
    }

    # Send the parsing JSON data
    requests.post(f"{api_url}/{api_device}/parse_license", json=parse_license_json_data, headers=x_headers)

    # Get the keys
    get_keys = requests.post(f"{api_url}/{api_device}/get_keys/ALL",
                             json={"session_id": session_id}, headers=x_headers)

    # Set DB keys
    db_keys = ''

    # Set mp4 decrypt keys
    mp4decrypt_keys = []

    for key in get_keys.json()["data"]["keys"]:
        if not key["type"] == "SIGNING":
            db_keys += f"{key['key_id']}:{key['key']}\n"
            mp4decrypt_keys.append('--key')
            mp4decrypt_keys.append(f"{key['key_id']}:{key['key']}\n")
            await key_cache(pssh=pssh, db_keys=db_keys)

    # Close the session
    requests.get(f"{api_url}/{api_device}/close/{session_id}", headers=x_headers)

    # Return keys if function is called from variable assignment
    return db_keys, mp4decrypt_keys


# Define function for encrypted video download
async def encrypted_video_download(manifest_url: str, res: str = None):
    # Create the encrypted filename for easy use
    random_encrypted_video_file_name = str(uuid.uuid4())

    # List of n_m3u8dl-re video downloads commands for best 1280x720p video
    video_nm3u8_720 = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sv',
        f'res="1280*":for=best',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_video_file_name}",
        "--log-level",
        "OFF"
    ]

    # List of n_m3u8dl-re video downloads commands for best 1920x1080p video
    video_nm3u8_1080 = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sv',
        f'res="1920*":for=best',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_video_file_name}",
        "--log-level",
        "OFF"
    ]

    # List of n_m3u8dl-re video downloads commands for best manual res video
    video_nm3u8_manual = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sv',
        f'res="{res}*":for=best',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_video_file_name}",
        "--log-level",
        "OFF"
    ]

    # Check if res option has been passed, if not auto download 1080p/720p
    if res is None:
        # Run n_m3u8dl-re from above list for best 1080p video if available
        subprocess.run(video_nm3u8_1080)
        # Find the encrypted video file path and extension
        try:
            encrypted_video_file_path_and_name = \
                glob.glob(f'{main_directory}\\downloads\\{random_encrypted_video_file_name}.*')[0]
            return encrypted_video_file_path_and_name
        # Add exception if video file isn't found / available in 1080p
        except IndexError:
            try:
                # Run n_m3u8dl-re from above list for best 720p video if available
                subprocess.run(video_nm3u8_720)
                encrypted_audio_file_path_and_name = \
                    glob.glob(f'{main_directory}\\downloads\\{random_encrypted_video_file_name}.*')[0]
                return encrypted_audio_file_path_and_name
            # If 720/1080p isn't available, return None value
            except:
                return None
    else:
        # Run n_m3u8dl-re from above list for specified res
        subprocess.run(video_nm3u8_manual)
        try:
            encrypted_video_file_path_and_name = \
                glob.glob(f'{main_directory}\\downloads\\{random_encrypted_video_file_name}.*')[0]
            return encrypted_video_file_path_and_name
        except:
            return None


# Define function for encrypted audio download
async def encrypted_audio_download(manifest_url: str, alang: str = None):
    # Create the encrypted filename for easy use
    random_encrypted_audio_file_name = str(uuid.uuid4())

    # List of n_m3u8dl-re best english audio commands
    audio_nm3u8_best_english = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sa',
        'lang=en:for=best',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_audio_file_name}",
        "--log-level",
        "OFF"
    ]

    # Create a general download in case english isn't available or properly tagged
    audio_nm3u8_best_general = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sa',
        'all',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_audio_file_name}",
        "--log-level",
        "OFF"
    ]

    # List of commands if audio is selected
    audio_nm3u8_manual = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-sa',
        f'{alang}',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_encrypted_audio_file_name}",
        "--log-level",
        "OFF"
    ]

    if alang is None:
        # Run n_m3u8dl-re from above list for best english audio
        subprocess.run(audio_nm3u8_best_english)
        try:
            encrypted_audio_file_path_and_name = \
                glob.glob(f'{main_directory}\\downloads\\{random_encrypted_audio_file_name}.*')[0]
            return encrypted_audio_file_path_and_name
        # If english is not found, download the best audio available
        except:
            try:
                subprocess.run(audio_nm3u8_best_general)
                encrypted_audio_file_path_and_name = \
                    glob.glob(f'{main_directory}\\downloads\\{random_encrypted_audio_file_name}.*')[0]
                return encrypted_audio_file_path_and_name
            # If n_m3u8dl-re can't find anything, return None value
            except:
                return None
    else:
        subprocess.run(audio_nm3u8_manual)
        # Run n_m3u8dl-re from above list for specified audio language
        try:
            encrypted_video_file_path_and_name = \
                glob.glob(f'{main_directory}\\downloads\\{random_encrypted_audio_file_name}.*')[0]
            return encrypted_video_file_path_and_name
        except:
            return None


# Define subtitle download function
async def subtitle_download(manifest_url: str, slang: str = None):
    # Create the encrypted filename for easy use
    random_subtitle_name = str(uuid.uuid4())

    # List of n_m3u8dl-re subtitle downloads commands
    subtitle_nm3u8_english = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-ss',
        'name="English":for=all',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_subtitle_name}",
        "--log-level",
        "OFF"
    ]

    subtitle_nm3u8_foreign = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-ss',
        'all',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_subtitle_name}",
        "--log-level",
        "OFF"
    ]

    subtitle_nm3u8_manual = [
        f"{n_m3u8dl_re}",
        f"{manifest_url}",
        '-ss',
        f'name="{slang}":for=all',
        "--tmp-dir",
        f"{main_directory}\\temp\\",
        "--save-dir",
        f"{main_directory}\\downloads\\",
        "--save-name",
        f"{random_subtitle_name}",
        "--log-level",
        "OFF"
    ]

    if slang is None:
        # Run n_m3u8dl-re from above list for subtitles
        subprocess.run(subtitle_nm3u8_english)

        # Find the subtitle path and extension
        try:
            subtitle_file_path_and_name = glob.glob(f'{main_directory}\\downloads\\{random_subtitle_name}.*')[0]
            return subtitle_file_path_and_name
        # If english is not available, download all.
        except:
            subprocess.run(subtitle_nm3u8_foreign)
            try:
                subtitle_file_path_and_name = glob.glob(f'{main_directory}\\downloads\\{random_subtitle_name}.*')[0]
                return subtitle_file_path_and_name
            # If no subtitles are found, return None value.
            except:
                return None
    else:
        subprocess.run(subtitle_nm3u8_manual)
        try:
            subtitle_file_path_and_name = glob.glob(f'{main_directory}\\downloads\\{random_subtitle_name}.*')[0]
            return subtitle_file_path_and_name
        # If no subtitles are found, return None value.
        except:
            return None


# Define function to decrypt files
async def decrypt_file(input_file_path_and_name: str, mp4decrypt_keys: list):
    # Get the encrypted filename and extension
    try:
        filepath, file_ext = os.path.splitext(input_file_path_and_name)
    # Send None value if not found
    except:
        return None

    # Set random file name for easy use
    random_decrypted_file_name = str(uuid.uuid4())

    # Set the mp4decrypt command
    mp4decrypt_command = [
        f'{mp4decrypt}',
        f'{filepath}{file_ext}',
        f'{main_directory}\\downloads\\{random_decrypted_file_name}{file_ext}'
        ] + mp4decrypt_keys

    # Run mp4decrypt
    subprocess.run(mp4decrypt_command)

    # set the decrypted file name and extension
    decrypted_file_path_and_name = f'{main_directory}\\downloads\\{random_decrypted_file_name}{file_ext}'

    # Remove the encrypted file
    os.remove(input_file_path_and_name)

    # Return the decrypted file path, name, and extension.
    return decrypted_file_path_and_name


# Define function to merge all decrypted files
async def ffmpeg_merge(input_video_file: str, input_audio_file: str, input_subtitle_file: str = None):
    # Assign a random name for easy use
    random_merge_name = f'{str(uuid.uuid4())}.mkv'

    # FFmpeg merge command if subtitles are present
    ffmpeg_merge_files_with_subtitles = [
        f"{ffmpeg}",
        '-i',
        f"{input_video_file}",
        '-i',
        f"{input_audio_file}",
        '-i',
        f"{input_subtitle_file}",
        '-vcodec',
        'copy',
        '-acodec',
        'copy',
        '-scodec',
        'copy',
        f"{main_directory}\\downloads\\{random_merge_name}",
        "-loglevel",
        "panic"
    ]

    # FFmpeg merge command if subtitles are not present
    ffmpeg_merge_files_without_subtitles = [
        f"{ffmpeg}",
        '-i',
        f"{input_video_file}",
        '-i',
        f"{input_audio_file}",
        '-vcodec',
        'copy',
        '-acodec',
        'copy',
        f"{main_directory}\\downloads\\{random_merge_name}",
        "-loglevel",
        "panic"
    ]

    # Check if there is any subtitles
    if input_subtitle_file is not None:
        try:
            # Merge if there are subtitles
            subprocess.run(ffmpeg_merge_files_with_subtitles)
            os.remove(input_video_file)
            os.remove(input_audio_file)
            os.remove(input_subtitle_file)
            return f'{main_directory}\\downloads\\{random_merge_name}'
        except:
            return None
    else:
        try:
            # Merge if there are no subtitles
            subprocess.run(ffmpeg_merge_files_without_subtitles)
            os.remove(input_video_file)
            os.remove(input_audio_file)
            return f'{main_directory}\\downloads\\{random_merge_name}'
        except:
            return None


# Define main function
async def main():
    # Get manifest from the user
    manifest = input(f"\nInput manifest URL: ")

    # Retrieve the PSSH
    print_pssh = await manifest_pssh_parse(manifest)

    # Print out the PSSH if found, else exit
    if print_pssh is not None:
        print(f'\nPSSH: {print_pssh}\n')

    license_url = input("License URL: ")

    # Retrieve and set decryption keys
    dbkeys, mp4decrypt_keys = await retrieve_keys_remotely(pssh=print_pssh, license_url=license_url)

    # Print out keys if exist, else exit
    if dbkeys != "":
        print(f"\nKeys found:\n{dbkeys}")
    else:
        print(f"\nCouldn't retrieve keys!")
        exit()

    # Downloading and assigning path/name for encrypted video using the encrypted_video_download function

    # Check if manual resolution was specified
    if args.video_res is not None:
        print(f"\nUser specified {args.video_res} resolution\n")
        encrypted_video_file_path_and_name = await encrypted_video_download(manifest_url=manifest, res=args.video_res)
    # Default if none specified
    else:
        encrypted_video_file_path_and_name = await encrypted_video_download(manifest_url=manifest)

    # Exit the process if failed
    if encrypted_video_file_path_and_name is None:
        print("Couldn't download video!")
        exit()
    # If exists, print filepath name/extension
    else:
        print(f"\nDownloaded encrypted video to {encrypted_video_file_path_and_name}")

    # Downloading and assigning path/name for encrypted audio using the encrypted_audio_download function

    # Check if audio language was manually specified
    if args.audio_lang is not None:
        print(f"\nUser specified {args.audio_lang} audio language\n")
        encrypted_audio_file_path_and_name = await encrypted_audio_download(manifest_url=manifest, alang=args.audio_lang)
    # Default if none specified
    else:
        encrypted_audio_file_path_and_name = await encrypted_audio_download(manifest_url=manifest)

    # Exit the process if failed
    if encrypted_audio_file_path_and_name is None:
        print("Couldn't download audio!")
        exit()
    # If exists, print filepath and name/extension
    else:
        print(f"\nDownloaded encrypted audio to {encrypted_audio_file_path_and_name}")

    # Downloading and assigning path/name for subtitles using the susbtitle_download function

    # Check if subtitle language was manually specified
    if args.subtitle_lang is not None:
        print(f"\nUser specified {args.subtitle_lang} subtitle language\n")
        subtitle_file_path_and_name = await subtitle_download(manifest_url=manifest, slang=args.subtitle_lang)
    # Default if none specified
    else:
        subtitle_file_path_and_name = await subtitle_download(manifest_url=manifest)

    # Print to the user no subtitles could be found
    if subtitle_file_path_and_name is None:
        print(f"\nCouldn't download subtitles!")
    # If exists, print filepath and name/extension
    else:
        print(f"\nDownloaded subtitles to {subtitle_file_path_and_name}")

    # Decrypting the encrypted video file with mp4decrypt function and mp4decrypt keys
    decrypted_video_file_path_and_name = await decrypt_file(input_file_path_and_name=encrypted_video_file_path_and_name,
                                                            mp4decrypt_keys=mp4decrypt_keys)
    # Exit the process if decryption failed
    if decrypted_video_file_path_and_name is None:
        print(f"\nVideo decryption failed!")
        exit()
    # If exists, print filepath and name/extension
    else:
        print(f"\nDecrypted video located at {decrypted_video_file_path_and_name}")

    # Decrypting the encrypted audio file with mp4decrypt function and mp4decrypt keys
    decrypted_audio_file_path_and_name = await decrypt_file(input_file_path_and_name=encrypted_audio_file_path_and_name,
                                                            mp4decrypt_keys=mp4decrypt_keys)
    # Exit the process if decryption failed
    if decrypted_audio_file_path_and_name is None:
        print(f"\nAudio decryption failed!")
        exit()
    # If exists, print filepath and name/extension
    else:
        print(f"\nDecrypted audio located at {decrypted_audio_file_path_and_name}")

    # Muxing the decrypted video/audio, and susbtitles if available with ffmpeg_merge function
    final_muxed_file_path_and_name = await ffmpeg_merge(input_video_file=decrypted_video_file_path_and_name,
                                                        input_audio_file=decrypted_audio_file_path_and_name,
                                                        input_subtitle_file=subtitle_file_path_and_name)
    # Exit the process if muxing failed
    if final_muxed_file_path_and_name is None:
        print(f"\nMuxing failed!")
        exit()
    # If exists, print filepath and name/extension
    else:
        print(f"\nFinal mux located at {final_muxed_file_path_and_name}")

# Run the main program
asyncio.run(main())
