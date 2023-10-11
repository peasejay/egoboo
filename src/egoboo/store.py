import difflib
import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship

#Base = declarative_base() 

class Base(DeclarativeBase):
     pass

class Store(Base):

  __tablename__ = "store"
  id: Mapped[int] = mapped_column(primary_key=True)
  code: Mapped[str] = mapped_column(String)
  content: Mapped[str] = mapped_column(String)
  last_checked: Mapped[datetime.datetime] = mapped_column(DateTime)
  last_updated: Mapped[datetime.datetime] = mapped_column(DateTime)
  expires: Mapped[datetime.datetime] = mapped_column(DateTime)


 
    