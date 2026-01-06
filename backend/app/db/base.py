from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
#from app.db.base import Base

# 👇 IMPORT MODELS HERE
# from app.models.user import User

# 👇 import all models AFTER Base definition
#import app.models

# Import ALL models here so Alembic can see them
#from app.models.user import User
#from app.models.job import Job
#from app.models.application import Application
