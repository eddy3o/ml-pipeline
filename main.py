from src.data_processing.cleaner import Cleaner
import src.utils.db_connector as db_connector

def main():
    # Define file paths and db needs
    adoptants_file_path = "data/raw/adoptantes.json"
    db_path = "data/processed/adoption_analysis.db"
    db_connector.run_migrations(db_path)

    """ 
    First Module: Data Cleaning  
    """
    cleaner = Cleaner(adoptants_file_path)
    db_connector.save_dataframe_to_table(cleaner.df, "adoption_analysis", db_path)

if __name__ == "__main__":
    main()