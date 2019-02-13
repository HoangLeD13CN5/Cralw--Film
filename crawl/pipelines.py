# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from crawl.models import FilmDB, WebDB, db_connect, create_table


class CrawlPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save deals in the database.

                This method is called for every item pipeline component.
                """
        session = self.Session()
        film = FilmDB()
        film.director = item["director"]
        film.kind = item["kind"]
        film.actors = item["actors"]
        film.des_Film = item["description"]
        film.duration = item["duration"]
        film.IMDb = item["imdb"]
        film.release_year = item["release_year"]
        film.thumbnail = item["thumbnail"]
        film.title = item["title"]
        film.title_english = item["title_english"]
        id_film = -1
        if item["title_english"]:
            search = item["title_english"]
            film = session.query(FilmDB).filter(FilmDB.title_english == search).first()
            if film:
                id_film = film.id
        else:
            search = item["title"]
            film = session.query(FilmDB).filter(FilmDB.title == search).first()
            id_film = -1
            if film:
                id_film = film.id
        print("Phim ID: " + str(id_film))
        if id_film != -1:
            return item
        session.add(film)
        session.close()
        return item

