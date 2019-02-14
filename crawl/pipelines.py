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
        film.type_film = item["type"]
        film.title_english = item["title_english"]
        web = WebDB()
        web.nameWeb = item["nameWeb"]
        web.status_Film = item["status"]
        web.urlFilm = item["url"]
        web.urlWeb = item["url_root"]
        web.views = item["views"]
        film.webs.append(web)
        result = session.query(FilmDB).filter(FilmDB.title == item["title"]).first()
        try:
            if result:
                result.director = item["director"]
                result.kind = item["kind"]
                result.actors = item["actors"]
                result.des_Film = item["description"]
                result.duration = item["duration"]
                result.IMDb = item["imdb"]
                result.release_year = item["release_year"]
                result.thumbnail = item["thumbnail"]
                result.title = item["title"]
                result.title_english = item["title_english"]
                result.webs.append(web)
            else:
                session.add(film)
            session.add(web)
            session.commit()
        except:
            print("An exception occurred")
        finally:
            session.close()
        return item

