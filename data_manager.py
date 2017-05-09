from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///Database.db")
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

def get(item, Id=None):

    # item as class
    
    session = Session()
    
    if Id == None:    
        return session.query(item).all()
    
    if Id is int:
        return session.query(item).filter(item.id == Id)
    
    if Id is list:
        return list(map(lambda x: session.query(item).filter(item.id == x), Id))
    
    else:
        raise TypeError

def save(items):
    
    # receives a single list of objects or a list of lists and saves it
    
    session = Session()
    
    if type(items[0]) is list:
    
        for item in items:
                
            session.bulk_save_objects(item)
    
    else:
                        
        session.bulk_save_objects(items)
            
    session.commit()

def delete(item):
    
    session = Session()
    
    Item = type(item)
    session.delete(session.query(Item).filter(Item.name==item.name).one())