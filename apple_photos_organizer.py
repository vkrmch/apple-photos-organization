import datetime
import calendar
import osxphotos

def main():
    photosdb = osxphotos.PhotosDB()
    photos = {}

    # find all photos for date range
    years = range(2000, int(datetime.datetime.now().strftime("%Y"))+1)
    months = range(1, 13)
    for year in years:
        for month in months:
            last_day_of_month = calendar.monthrange(year, month)[1]
            p = photosdb.query(
                osxphotos.QueryOptions(
                    from_date=datetime.datetime(year=year, month=month, day=1),
                    to_date=datetime.datetime(year=year, month=month, day=last_day_of_month)
                )
            )

            count = len(p)
            if count > 0:
                album_name = f"{year}.{month:02}"
                print(f"adding {count} photos to album {album_name}")
                album = osxphotos.PhotosAlbum(album_name)
                album.extend(p)

                if not photos.get(year):
                    photos[year] = {}

                if not photos.get(year).get(month):
                    photos[year][month] = {}

                photos[year][month] = len(album.photos())

    # count in albums
    print("printing final counts")
    for year, months in photos.items():
        for month, count in months.items():
                print(f"{year}.{month:02} {count:10}")

if __name__ == "__main__":
    main()