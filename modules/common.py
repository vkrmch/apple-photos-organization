import osxphotos
import photoscript
import logging as pylogging
from gpm import logging

log = logging.get_logger(logger_name=__name__)

def disable_osxphotos_logger():
    # disable logger from osxphotos (have to do everytime the library is used)
    log_ = pylogging.getLogger()
    log_.disabled = True
    log_.removeHandler(log_.handlers[0])

def get_apdb():
    db = osxphotos.PhotosDB()
    disable_osxphotos_logger()
    return db

def get_aplib():
    lib = photoscript.PhotosLibrary()
    lib.activate()
    lib.hide()
    log.info(f"running photos app version: {lib.version}")

    return lib

def get_photos(apdb):
    top_level_folders = apdb.folder_info
    folders = []

    for top_level_folder in top_level_folders:
        folder_dict = top_level_folder.asdict()

        folder = {
            "name": folder_dict["title"],
            "uuid": folder_dict["uuid"],
            "parent": folder_dict["parent"],
            "subfolders": []
        }

        if len(folder_dict["subfolders"]) > 0:
            for sub_folder_uuid in folder_dict["subfolders"]:
                sub_folder_dict = osxphotos.FolderInfo(db=apdb, uuid=sub_folder_uuid).asdict()

                sub_folder = {
                    "name": sub_folder_dict["title"],
                    "uuid": sub_folder_dict["uuid"],
                    "parent": sub_folder_dict["parent"],
                    "albums": []
                }

                if len(sub_folder_dict["albums"]) > 0:
                    for album_uuid in sub_folder_dict["albums"]:
                        album_obj = osxphotos.AlbumInfo(db=apdb, uuid=album_uuid)
                        album_dict = album_obj.asdict()

                        album = {
                            "name": album_dict["title"],
                            "uuid": album_dict["uuid"],
                            "parent": album_dict["parent"],
                            "photos": album_obj.photos
                        }
                        sub_folder["albums"].append(album)

                folder["subfolders"].append(sub_folder)

        folders.append(folder)

    albums = []
    all_albums = apdb.album_info  # the property returns all albums not top level
    for album_obj in all_albums:
        album_dict = album_obj.asdict()
        album = {
            "name": album_dict["title"],
            "uuid": album_dict["uuid"],
            "parent": album_dict["parent"],
            "photos": album_obj.photos
        }

        if len(album["parent"]) == 0:
            albums.append(album)

    return folders, albums