
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
# Only register the succesful entrances
class gateHistory(Base):
    __tablename__ = 'gateHistory'
    id_gate_occurence = Column(Integer,primary_key=True)
    gate_id = Column(String)
    Status = Column(String)
    Date = Column(Date)
    def __repr__(self):
        return "<gateHistory(id_gate_occurence='%d' gate_id='%s' Status='%s' Date='%s')>" % (
                                self.id_gate_occurence,self.gate_id,self.Status,self.Date)
    def to_dictionary(self):
        return {"id_gate_occurence": self.id_gate_occurence, "gate_id": self.gate_id, "Status": self.Status,"Date": self.Date}


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Query to List Table
def getgateHistory():
    return session.query(gateHistory).all()

def listuserHistoryDICT():
    ret_list = []
    lv = getgateHistory()
    for v in lv:
        vd = v.to_dictionary()
        del(vd["id_gate_occurence"])
        del(vd["gate_id"])
        del(vd["Status"])
        del(vd["Date"])
        ret_list.append(vd)
    return ret_list
# Query to add elements
def newOcurrence(new_id_gate_occurence, new_gate_id, new_Status,new_Date):
    aux = CheckOccurrenceID(new_id_gate_occurence)
    if aux:
        return 0
    else:
        auth = gateHistory(id_gate_occurence = new_id_gate_occurence, gate_id = new_gate_id, Status=new_Status,Date=new_Date)
        session.add(auth)
        try:
            session.commit()
        except:
            session.rollback()
        return 1

# See if ID already Exists
def CheckOccurrenceID(new_id_gate_occurence):
    return session.query(gateHistory).filter(gateHistory.id_gate_occurence==new_id_gate_occurence).first() is not None

# Get gate info
def GetGateOccurrences(new_gate_id):
    return session.query(gateHistory).filter(gateHistory.gate_id==new_gate_id).all()
    
# # Get gate info
# def GetOccurrencesFrom(date_check):
#     return session.query(userTable).filter(userTable.Date > date_check).all()
    
