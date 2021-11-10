
##################### Library Imports for SQL Alchemy #####################

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------GATE DATA-----------------
# ----------------------------------------


#SLQ access layer initialization
DATABASE_FILE = "gate_db_rep.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    # print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls

Base = declarative_base()


#Declaration of data

class GateTable(Base):
    __tablename__ = 'GateTable'
    id = Column(Integer,primary_key=True)
    location = Column(String)
    secret_number = Column(Integer)
    activation_number = Column(Integer,default=0)
    def __repr__(self):
        return "<GateTable(id='%d' location='%s' secret_number='%d' activation_number='%d')>" % (
                                self.id,self.location,self.secret_number,self.activation_number)


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Query to List Table
def getGates():
    return session.query(GateTable).all()

# Query to add elements
def newGate(new_id, new_location, new_secret_number, new_activation_number):
    aux = CheckGateID(new_id)
    if aux:
        return 0
    else:
        auth = GateTable(id = new_id, location = new_location, secret_number=new_secret_number,activation_number=new_activation_number)
        session.add(auth)
        try:
            session.commit()
        except:
            session.rollback()
        return 1

# See if ID already Exists
def CheckGateID(gate_id):
    return session.query(GateTable).filter(GateTable.id==gate_id).first() is not None

# Get gate info
def GetGate(gate_id):
    return session.query(GateTable).filter(GateTable.id==gate_id).all()

# Delete Specific Gate
def DeleteGate(gate_id):
    aux = CheckGateID(gate_id)
    if aux:
        session.query(GateTable).filter(GateTable.id==gate_id).delete()
        try:
                session.commit()
        except:
                session.rollback()
        return  1
    else:
        return 0

# Replace Activation Code
def UpdateGateActCode(gate_id):
    aux = CheckGateID(gate_id)
    if aux:
        session.query(GateTable).filter(GateTable.id==gate_id).first().activation_number += 1
        try :
            session.commit()
        except:
            session.rollback()
        return 1
    else:
        return 0
    
# get Activations Number
def CheckActivationsNumber(gate_id):
    return session.query(GateTable.activation_number).filter(GateTable.id==gate_id).all()

# Check if Secret Number exists
def SecretExist(secret_number):
    return session.query(GateTable).filter(GateTable.secret_number==secret_number).first() is not None

# Check Secret Number
def CheckSecret(gate_id,secret):
    return session.query(GateTable).filter(GateTable.id==gate_id,GateTable.secret_number==secret).first() is not None
