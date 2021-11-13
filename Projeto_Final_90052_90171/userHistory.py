
##################### Library Imports for SQL Alchemy #####################

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import sessionmaker

# -- ADINT Final Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------User History--------------
# ----------------------------------------


#SLQ access layer initialization
DATABASE_FILE = "userhist_db.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    # print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls

Base = declarative_base()


#Declaration of data
# Only register the succesful entrances
class userHistory(Base):
    __tablename__ = 'userHistory'
    id_user_occurence = Column(Integer,primary_key=True)
    user = Column(String)
    gate_id = Column(String)
    Date = Column(DateTime)
    def __repr__(self):
        return "<userHistory(id_user_occurence='%d' user='%s' gate_id='%d' Date='%s')>" % (
                                self.id_user_occurence,self.user,self.gate_id,self.Date)
    def to_dictionary(self):
        return {"id_user_occurence": self.id_user_occurence, "user": self.user, "gate_id": self.gate_id,"Date": str(self.Date)}


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Query to List Table
def getuserHistory():
    return session.query(userHistory).all()


def listuserHistoryDICT():
    ret_list = []
    lv = getuserHistory()
    for v in lv:
        vd = v.to_dictionary()
        del(vd["id_user_occurence"])
        del(vd["user"])
        del(vd["gate_id"])
        del(vd["Date"])
        ret_list.append(vd)
    return ret_list

# Query to add elements
def newOcurrence(new_user, new_gate_id,new_Date):
    auth = userHistory(user = new_user, gate_id=new_gate_id,Date=new_Date)
    session.add(auth)
    try:
        session.commit()
    except:
        session.rollback()
    return 1

# See if ID already Exists
def CheckOccurrenceID(new_id_user_occurence):
    return session.query(userHistory).filter(userHistory.id_user_occurence==new_id_user_occurence).first() is not None

# Get user info
def GetUserOccurrences(new_user):
    return session.query(userHistory).filter(userHistory.user==new_user).all()
    


