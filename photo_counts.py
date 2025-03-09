import datetime
import calendar
import argparse
import logging as pylogging
import osxphotos
from gpm import logging
from modules import common

log = logging.Log(script=__file__, logger_name=__name__, log_level=pylogging.DEBUG)
# disable osxphotos logger
common.disable_osxphotos_logger()

def main(years=None):
    apdb = common.get_apdb()
    folders, albums = common.get_photos(apdb)
    photos = {}

    for folder in folders:
        folder_name = folder["name"]
        photos[folder_name] = {}
        for subfolder in folder["subfolders"]:
            subfolder_name = subfolder["name"]
            photos[folder_name][subfolder_name] = {}
            for album in subfolder["albums"]:
                album_name = album["name"]
                count = len(album["photos"])
                photos[folder_name][subfolder_name][album_name] = count
                log.info(f"{folder_name}/{subfolder_name}/{album_name} {count:10}")

"""    for folder_name, subfolder in photos.items():
        for subfolder_name, albums in subfolder.items():
            for album_name, count in albums.items():
                log.info(f"{folder_name}/{subfolder_name}/{album_name} {count:10}")"""

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("-y", "--years", help="4 digit year, separate multiple years by commas")
    args = argp.parse_args()

    log.start()
    main(years=args.years)
    log.end()