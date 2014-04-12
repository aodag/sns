import hashlib
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import (
    relationship,
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

    def has_profile(self):
        return len(self.profiles)

    def new_profile(self, *args, **kwargs):
        return UserProfile(user=self,
                           *args, **kwargs)


class UserProfile(Base):
    __tablename__ = 'userprofiles'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    given_name = Column(Unicode(255))
    family_name = Column(Unicode(255))
    nick = Column(Unicode(255))
    gender = Column(Enum('male', 'female', name="gender"))
    plan = Column(UnicodeText)
    user = relationship(User, backref='profiles')

    def add_image(self, image):
        data = image.tostring()
        return UserProfileImage(user_profile=self,
                                user=self.user,
                                data=data)


class UserProfileImage(Base):
    __tablename__ = 'userprofileimages'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey('userprofiles.id'))
    user_profile = relationship('UserProfile',
                                backref="images")

    data = Column(LargeBinary)
