import os
import re
from collections import defaultdict

import yt_dlp
import argparse
import time

from datetime import datetime, timedelta
from pathlib import Path

from sconfig import parse_config_with_fallbacks, parse_config_with_overrides

from yt_dlp import YoutubeDL
from colorama import Fore, Style

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
    sleep_interval = 1

    config = parse_config_with_overrides(section="download", params=[("link", str, link), ("output", str, output),
                                                                     ("filetype", str, filetype)])
    link, output, filetype = config["link"], config["output"], config["filetype"]

    while link is None:
        link = input("Playlist link: ")

    while output is None:
        output = input("Output directory: ").strip('"')

    if filetype is None:
        filetype = "mp3"

    if quiet is None:
        quiet = True

    playlist_info = get_playlist_info(link)

    if playlist_info:
        title = playlist_info.get("title")
        song_count = playlist_info.get("playlist_count")
        print(f"{Fore.GREEN}{title}{Style.RESET_ALL} has {song_count} songs")

    songs: defaultdict[str, str] = defaultdict(str)

    for song_info in playlist_info.get("entries", []):
        title = song_info.get("title")
        id = song_info.get("id")
        songs[title] = id

    print(f"Found data for {len(songs)} songs")

    downloaded_songs: defaultdict[str, str] = defaultdict(str)
    to_download: defaultdict[str, str] = defaultdict(str)

    existing_files = list(normalize_string(track.stem) for track in Path(output).rglob("*.mp3"))

    for song in songs.keys():
        if normalize_string(song) in existing_files:
            downloaded_songs[song] = songs[song]
        else:
            to_download[song] = songs[song]

    if len(downloaded_songs) > 0:
        update_cache = ""

        while update_cache == "" or update_cache == "r":
            update_cache = input(
                f"It looks like there are {Fore.GREEN}{len(downloaded_songs)}{Style.RESET_ALL} songs in {Fore.CYAN}{output}{Style.RESET_ALL}. {Fore.LIGHTMAGENTA_EX}Wanna update downloaded.txt?{Style.RESET_ALL} (y/n/r): ").lower()

            if update_cache == "r":
                do_display = input(
                    f"{Fore.YELLOW}Display {len(to_download)} undownloaded tracks?{Style.RESET_ALL} (y/n): ").lower()

                if do_display != "y":
                    continue

                for song in to_download.keys():
                    print(song)

        num_lines = 0

        with open("downloaded.txt", "w", encoding="utf-8") as file:
            if update_cache == "y":
                for song_id in downloaded_songs.values():
                    file.write(f"youtube {song_id}\n")

                print("Updated downloaded.txt")

        with open("downloaded.txt", "r", encoding="utf-8") as file:
            num_lines = len(file.readlines())

        print(
            f"{Fore.GREEN}{num_lines}{Style.RESET_ALL} tracks will be ignored during download, what a time saver!")

    proceed = input("Start downloads? (y/n): ").lower()

    if proceed != "y":
        return

    now = datetime.now()
    total_seconds = sleep_interval * len(to_download)
    estimated_completion_time = now + timedelta(seconds=total_seconds)

    print(
        f"Downloading {Fore.CYAN}{len(to_download)}{Style.RESET_ALL} tracks. {Fore.CYAN}Estimated completion time: {estimated_completion_time}{Style.RESET_ALL}")

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
        "sleep_interval": sleep_interval,
        "ignoreerrors": True,
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


def normalize_string(input):
    input = input.lower()
    input = re.sub(r"[^a-z0-9\s()-]", "", input)
    input = re.sub(r"\s+", "", input)
    input = input.strip()
    return input


if __name__ == '__main__':
    download_playlist()