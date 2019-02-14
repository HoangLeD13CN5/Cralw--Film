from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Text)

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
    __tablename__ = "FilmDB"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(255), unique=True)
    title_english = Column('title_english', String(255), unique=True, nullable=True)
    thumbnail = Column('thumbnail', String(255))
    kind = Column('kind', Text())
    type_film = Column('type_film', Integer)
    duration = Column('duration', Text())
    actors = Column('actors', Text())
    director = Column('director', Text())
    release_year = Column('release_year', Text())
    des_Film = Column('des_Film', Text())
    IMDb = Column('IMDb', Text())
    webs = relationship('WebDB', back_populates="film")


class WebDB(DeclarativeBase):
    __tablename__ = "WebDB"
    id = Column(Integer, primary_key=True, autoincrement=True)
    urlWeb = Column('urlWeb', String(255))
    nameWeb = Column('nameWeb', String(255))
    status_Film = Column('status_Film', Text())
    views = Column('views', Text())
    urlFilm = Column('urlFilm', String(255), unique=True)
    id_Film = Column(Integer, ForeignKey(FilmDB.id))
    film = relationship('FilmDB', back_populates="webs")
