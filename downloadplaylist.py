import json
import os
import yt_dlp
import argparse
import time

from pathlib import Path

from sconfig import parse_config_with_fallbacks

from yt_dlp import YoutubeDL

def get_playlist_info(link):
    info_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "dump_single_json": True
    }

    print("Getting playlist data...")

    info_dict = None

    with YoutubeDL(info_opts) as ydl:
        try:
            info_dict = ydl.extract_info(link, download=False)
        except Exception as e:
            print(f"Couldn't get playlist data: {e}")

    return info_dict

def download_playlist():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", type=str, help="Playlist link. Required")
    parser.add_argument("-o", "--output", type=str, help="Output directory. Required")
    parser.add_argument("-f", "--filetype", type=str, help="The format of the output files. Default: mp3")
    parser.add_argument("-q", "--quiet", type=bool, help="Whether the downloader doesn't print logs. Default: True")

    args = parser.parse_args()

    link = args.link
    output = args.output
    filetype = args.filetype
    quiet = args.quiet

    config = parse_config_with_fallbacks(section="download", params=[("link", str, link), ("output", str, output), ("filetype", str, filetype)])
    link, output, filetype = config["link"], config["output"], config["filetype"]

    while link is None:
        link = input("Playlist link: ")

    while output is None:
        output = input("Output directory: ").strip('"')

    if filetype is None:
        filetype = "mp3"

    if quiet is None:
        quiet = True

    # if Path(output).is_dir():
    #     deletion_confirmation = input(f"The directory {output} already exists. Music already present there will be skipped. Continue? (y/n): ")
    #
    #     if deletion_confirmation.lower() != "y":
    #         return

    input("Continue?")

    playlist_info = get_playlist_info(link)

    if playlist_info:
        print(f"{playlist_info.get("title")}'s info (found {playlist_info.get("playlist_count")} songs):")
        print(json.dumps(playlist_info, indent=4))

    input("Continue?")

    download_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": filetype,
        "outtmpl": os.path.join(output, "%(title)s.%(ext)s"),
        "noplaylist": False,
        "quiet": quiet,
        "no_warnings": quiet,
        "download_archive": "downloaded.txt",
        "progress_hooks": [hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": filetype,
            "preferredquality": "192"
        }]
    }

    queue_download(link, download_opts)

def queue_download(link: str, ydl_opts: dict, sleep_for: int = 1):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([link])
            except:
                print(f"Process most likely rate limited, trying again in {int(sleep_for)} second(s).")

                time.sleep(sleep_for)
                queue_download(link, ydl_opts, sleep_for * 2)

                return
        print(f"Successfully downloaded {link}")
    except Exception as e:
        print(f"An error occurred while trying to download the playlist: {e}")

def hook(d):
    if d["status"] == "finished":
        filename = Path(d["filename"]).stem
        print(f" Downloaded {filename}")

if __name__ == '__main__':
    download_playlist()