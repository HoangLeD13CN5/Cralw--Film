from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import relationship

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class FilmDB(DeclarativeBase):
    __tablename__ = "table_film"
    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    title_english = Column('title_english', Text())
    thumbnail = Column('thumbnail', Text())
    kind = Column('kind', Text())
    duration = Column('duration', Text())
    actors = Column('actors', Text())
    director = Column('director', Text())
    release_year = Column('release_year', Text())
    des_Film = Column('des_Film', Text())
    IMDb = Column('IMDb', Text())
    # webs = relationship("WebDB")


class WebDB(DeclarativeBase):
    __tablename__ = "table_web"
    id = Column(Integer, primary_key=True)
    urlWeb = Column('urlWeb', Text())
    nameWeb = Column('nameWeb', Text())
    status_Film = Column('status_Film', Text())
    views = Column('views', Text())
    urlFilm = Column('urlFilm', Text())
    id_Film = Column('id_Film', Integer, ForeignKey("table_film.id"), nullable=False)
