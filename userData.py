
##################### Library Imports for SQL Alchemy #####################

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------GATE DATA-----------------
# ----------------------------------------


#SLQ access layer initialization
DATABASE_FILE = "database.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    # print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls

Base = declarative_base()


#Declaration of data

class userTable(Base):
    __tablename__ = 'userTable'
    user_id = Column(Integer,primary_key=True)
    token = Column(String)
    secret_code = Column(String)
    def __repr__(self):
        return "<userTable(user_id='%d' token='%s' secret_code='%s')>" % (
                                self.user_id,self.token,self.secret_code)
    def to_dictionary(self):
        return {"user_id": self.user_id, "token": self.token, "secret_code": self.secret_code}


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Query to List Table
def getuser():
    return session.query(userTable).all()

def listuserDICT():
    ret_list = []
    lv = getuser()
    for v in lv:
        vd = v.to_dictionary()
        del(vd["user_id"])
        del(vd["token"])
        del(vd["secret_code"])
        ret_list.append(vd)
    return ret_list
# Query to add elements
def newUser(new_user_id, new_oken, new_secret_code):
    aux = CheckuserID(new_user_id)
    if aux:
        return 0
    else:
        auth = userTable(user_id = new_user_id, token = new_oken, secret_code=new_secret_code)
        session.add(auth)
        try:
            session.commit()
        except:
            session.rollback()
        return 1

# See if ID already Exists
def CheckuserID(new_user_id):
    return session.query(userTable).filter(userTable.user_id==new_user_id).first() is not None

# Get gate info
def GetUserOccurrences(user_check):
    return session.query(userTable).filter(userTable.user_id==user_check).all()
    
# # Get gate info
# def GetOccurrencesFrom(date_check):
#     return session.query(userTable).filter(userTable.Date > date_check).all()
    
