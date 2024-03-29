
##################### Library Imports for SQL Alchemy #####################

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# -- ADINT Final Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------USER DATA-----------------
# ----------------------------------------
#


#SLQ access layer initialization
DATABASE_FILE = "user_db.sqlite"
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
    creation_time = Column(DateTime)
    def __repr__(self):
        return "<userTable(user_id='%d' token='%s' secret_code='%s' creation_time='%s')>" % (
                                self.user_id,self.token,self.secret_code,str(self.creation_time))
    def to_dictionary(self):
        return {"user_id": self.user_id, "token": self.token, "secret_code": self.secret_code, "creation_time": str(self.creation_time)}


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
def newUser(new_user_id, new_token, new_secret_code):
    aux = CheckuserID(new_user_id)
  
    if aux:
        return 0
    else:
        time = datetime.now() - timedelta(hours=1)

        auth = userTable(user_id = new_user_id, token = str(new_token), secret_code=new_secret_code, creation_time = time)
        session.add(auth)
        try:
            session.commit()
        except:
            session.rollback()
        return 1

# See if ID already Exists
def CheckuserID(new_user_id):
    return session.query(userTable).filter(userTable.user_id==new_user_id).first() is not None
def CheckuserToken(new_user_token):
    return session.query(userTable).filter(userTable.token==new_user_token).first() is not None

# Get User info
def GetUserOccurrences(user_check):
    return session.query(userTable).filter(userTable.user_id==user_check).all()

# Get user by Activation code
def GetUserbyAC(code):
    return session.query(userTable).filter(userTable.secret_code==code).first()

# Replace Token Code
def UpdateuserToken(user_id,new_token):
    aux = CheckuserID(user_id)
    if aux:
        session.query(userTable).filter(userTable.user_id==user_id).first().token = new_token
        try :
            session.commit()
        except:
            session.rollback()
        return 1
    else:
        return 0

# Replace Activation Code
def UpdateuserSecret(user_id,new_secret,delay=0):
    aux = CheckuserID(user_id)
    if aux:
        user = session.query(userTable).filter(userTable.user_id==user_id).first()
        user.secret_code = new_secret
        user.creation_time = datetime.now() - timedelta(hours=delay)
        try :
            session.commit()
        except:
            session.rollback()
        return 1
    else:
        return 0


def CheckCreaTime(user_id):
    user = session.query(userTable).filter(userTable.user_id==user_id).first()

    if user:
        delta = datetime.now() - user.creation_time
        if delta.days > 0 or delta.seconds > 60:
            return 0
        else:
            return 1
    return 0

    
