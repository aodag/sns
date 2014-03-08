import hashlib
from sqlalchemy import (
    Column,
    Integer,
    String,
    Unicode,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))


Base = declarative_base()


def init(engine, create=False):
    DBSession.remove()
    DBSession.configure(bind=engine)
    if create:
        Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    email = Column(Unicode(255), unique=True)
    username = Column(Unicode(255), unique=True)
    password_hash = Column(String(40))

    def _hash(self, password):
        return hashlib.sha1(password.encode('utf-8')).hexdigest()

    def set_password(self, password):
        self.password_hash = self._hash(password)

    password = property(fset=set_password)

    def verify_password(self, password):
        return self.password_hash == self._hash(password)
