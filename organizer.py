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

def main(years=None, rebuild=False, start_year=2000):
    if years is None:
        years = range(start_year, int(datetime.datetime.now().strftime("%Y"))+1)
    else:
        years = [int(y) for y in years.split(',')]

    months = range(1, 13)

    # get library and database
    aplib = common.get_aplib()
    apdb = common.get_apdb()

    # find all folders, and albums
    folders, albums = common.get_photos(apdb=apdb)
    log.info(f"top level folder count: {len(folders)}")
    log.info(f"top level album count: {len(albums)}")

    # if rebuild, remove folders and albums, don't worry no images are deleted
    # only delete if the name is in the Year, so any other albums manually created won't be affected
    if rebuild and (len(folders) > 0 or len(albums) > 0):
        # remove folders
        for folder in folders:
            if folder["name"].isdigit():
                if int(folder["name"]) in years:
                    folder_obj = aplib.folder(name=folder["name"])
                    log.info(f"removing folder, any sub-folders, and albums: {folder["name"]}")
                    aplib.delete_folder(folder=folder_obj)

        # remove top level albums
        for album in albums:
            if album["name"].isdigit():
                if int(album["name"]) in years:
                    album_obj = aplib.album(album["name"])
                    log.info(f"removing album: {album['name']}")
                    aplib.delete_album(album=album_obj)

        # refresh photodb
        apdb = common.get_apdb()

    # create folder structure, Year (Folder) > Month (Sub Folder) > Day (Album)
    photos = {}
    for year in years:
        for month in months:
            first_day_of_month = 1
            last_day_of_month = calendar.monthrange(year, month)[1]
            days = range(first_day_of_month, last_day_of_month + 1)

            for day in days:
                from_date = datetime.datetime(year, month, day)
                to_date = from_date + datetime.timedelta(days=1)

                # get all the photos from db
                p = apdb.query(
                    osxphotos.QueryOptions(
                        from_date=from_date,
                        to_date=to_date
                    )
                )

                count = len(p)
                log.info(f"processing year: {year}, month: {month}, day: {day}, count: {count}")

                if count > 0:
                    folder_name = f"{year}"
                    subfolder_name = f"{month:02}"
                    album_name = f"{folder_name}.{subfolder_name}.{day:02}"
                    album_name_fq = f"{folder_name}/{subfolder_name}/{album_name}"

                    if photos.get(folder_name) is None:
                        photos[folder_name] = {}

                    if photos.get(folder_name).get(subfolder_name) is None:
                        photos[folder_name][subfolder_name] = {}

                    if photos.get(folder_name).get(subfolder_name).get(album_name) is None:
                        photos[folder_name][subfolder_name][album_name] = 0

                    # get photo count
                    photo_count = len(
                        apdb.query(
                            osxphotos.QueryOptions(
                                album = [album_name]
                            )
                        )
                    )
                    log.info(f"existing photo count in album {album_name_fq}: {photo_count}")

                    if photo_count != count:
                        log.info(f"adding {count} photos to album {album_name_fq}")
                        album = osxphotos.PhotosAlbum(name=album_name_fq, split_folder="/")
                        album.extend(p)

                        photos[folder_name][subfolder_name][album_name] = photo_count
                    else:
                        log.info(f"not adding any photos since counts are same")


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("-r", "--rebuild", action="store_true", default=False, help="rebuild folder structure")
    argp.add_argument("-y", "--years", help="4 digit year, separate multiple years by commas")
    argp.add_argument("-sy", "--start_year", help="4 digit year to start from, if --years is specified, this is ignored, default: 2000")
    args = argp.parse_args()

    log.start()
    main(years=args.years, rebuild=args.rebuild, start_year=args.start_year)
    log.end()