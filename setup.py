from setuptools import setup


requires = [
    "pyramid",
    "pyramid_tm",
    "pyramid_layout",
    "pyramid_deform",
    "pyramid_mailer",
    "pyramid_mako",
    "sqlalchemy",
    "zope.sqlalchemy",
    "webhelpers2>=2.0b5",
    "deform>=2.0dev",
    "colander",
    "pillow",
    "pytz",
    "babel",
]

setup(name="sns",
      install_requires=requires,
      packages=["sns"],
      )
