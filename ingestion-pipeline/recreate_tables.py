from db_setup import Base, engine
from models import ResourceLink  # Import the model to ensure it's registered

def recreate_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables with new schema...")
    Base.metadata.create_all(bind=engine)
    print("Database tables have been recreated successfully!")

if __name__ == "__main__":
    recreate_tables()
