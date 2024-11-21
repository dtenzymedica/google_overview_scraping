import json
import logging
import os
import re
import hashlib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Text, VARCHAR
from sqlalchemy.orm import declarative_base, sessionmaker

# Setting up Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Loading credentials from db_config.json
try: 
    with open('/Users/d.tanubudhi/Documents/google_scraping/db_config.json') as config_file:
        config = json.load(config_file)

    user = config['user']
    password = config['password']
    host = config['host']
    port = config['port']
    database = config['database']
except Exception as e:
    logging.error(f"Error loading Database Credentials: {e}")
    raise

# Define the SQLAlchemy connection string for MariaDB using pymysql
connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'

# Creating the DATABASE ENGINE
try:
    engine = create_engine(connection_string)
    logging.info("Database engine created successfully.")
except Exception as e:
    logging.error(f"Error creating database engine: {e}")
    raise

# Define the base class
Base = declarative_base()

# Google Overview Table Definition
class OverViewAI(Base):
    __tablename__ = 'overview_ai'
    segment_hash = Column(Text, primary_key=True)
    segment_title = Column(Text)
    summary = Column(Text)
    urls = Column(Text)

# Create all tables in the database (if not already present)
Base.metadata.create_all(engine)

# Define session
Session = sessionmaker(bind=engine)

def get_latest_files(data_folder):
    """Automatically get the latest product and review CSV files from the data folder"""
    scrape_overview_path = None

    try:
        files = os.listdir(data_folder)

        # Filter files using regex to extract dates
        scraping_files = [(f, re.search(r'\d{4}-\d{2}-\d{2}', f)) for f in files if f.startswith('google-overviewai') and f.endswith('.csv')]
        
        # Extract files that have valid dates and parse the date for sorting
        scraping_files = [(f[0], datetime.strptime(f[1].group(), '%Y-%m-%d')) for f in scraping_files if f[1]]

        # Sort files by date in descending order
        scraping_files.sort(key=lambda x: x[1], reverse=True)

        # Get the latest file path
        if scraping_files:
            scrape_overview_path = os.path.join(data_folder, scraping_files[0][0])

        if not scrape_overview_path:
            raise FileNotFoundError('Could not find CSV file path in the specified folder.')
        
        return scrape_overview_path
    
    except Exception as e:
        logging.error(f"Error finding CSV file in the folder {data_folder}: {e}")
        raise

def generate_hash(title):
    """Generate MD5 hash of the title"""
    return hashlib.md5(title.encode('utf-8')).hexdigest()

def insert_data_to_db(scrape_overview_path):
    """Insert scraped data into the database"""

    session = Session()

    try: 
        # Load CSV data
        data_f = pd.read_csv(scrape_overview_path)
        logging.info("CSV loaded successfully.")

        # Replace NaN with None for SQL compatibility
        data_f = data_f.where(pd.notnull(data_f), None)

    except Exception as e:
        logging.error(f"Error loading CSV data: {e}")
        return
    
    try:
        # Prepare data to insert
        data_to_insert = []
        for _, row in data_f.iterrows():
            try:
                if row['segment_title']:
                    segment_hash = generate_hash(row['segment_title'].lower())
                else:
                    logging.warning(f"Missing segment_title for row {row}")
                existing_segment = session.query(OverViewAI).filter_by(segment_hash=segment_hash).first()

                if existing_segment is None:
                    data_to_insert.append(OverViewAI(
                        segment_hash=segment_hash,
                        segment_title=row['segment_title'],
                        summary=row['summary'],
                        urls=row['urls']
                    ))
            except Exception as row_e:
                logging.error(f"Error processing row: {row} - {row_e}")
        
        if data_to_insert:
            session.bulk_save_objects(data_to_insert)

        # Commit the transaction
        session.commit()
        logging.info(f"Data inserted successfully! Inserted {len(data_to_insert)} segments")
    
    except Exception as e:
        session.rollback()
        logging.error(f"Error inserting data: {e}")

    finally:
        session.close()
        logging.info("Session closed.")

data_folder = '/Users/d.tanubudhi/Documents/google_scraping/Data'

try:
    scrape_overview_path = get_latest_files(data_folder)
    insert_data_to_db(scrape_overview_path)
except Exception as e:
    logging.error(f"Error in the 'insert_data_to_db' function: {e}")
