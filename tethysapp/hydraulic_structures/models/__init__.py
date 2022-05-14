from tethysext.atcore.models.app_users import initialize_app_users_db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TestTable(Base):
    __tablename__ = 'test_table'

    # Columns
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    another_number = Column(Float)
    string = Column(String)


def init_primary_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    Base.metadata.create_all(engine)
    
    # Initialize app users tables
    initialize_app_users_db(engine, first_time)
    
    if first_time:
        # Make session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Initialize database with two dams
        test = TestTable(
            number=10,
            another_number=50.25,
        )

        # Add the dams to the session, commit, and close
        session.add(test)
        session.commit()
        session.close()
