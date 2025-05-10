import sys
import os
from src.data_processing.cleaner import Cleaner
import src.utils.db_connector as db_connector
import streamlit as st


current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from data_collection.scrape import scrape_website

def main():
    st.title('AI Web Scraper! - Para datos de adopciones.')
    
    
    mode = st.sidebar.selectbox("Seleccionar modo:", ["Scraping", "Procesamiento de datos"])

    if mode == "Scraping":
        # Modo scraping pew pew !!! trrratatatatata
        url = st.text_input('URL:')
        if st.button('Scrape'):
            st.write('Scraping the URL...')
            result = scrape_website(url)  
            if result:
                st.write(result) 
            else:
                st.write("No se pudo extraer contenido de la página.")
    
    elif mode == "Procesamiento de datos":
        # Modo procesamiento **PENDIENTE**
        adoptants_file_path = "data/raw/adoptantes.json"
        db_path = "data/processed/adoption_analysis.db"
        
        if st.button("Ejecutar procesamiento"):
            with st.spinner("Procesando datos..."):
                db_connector.run_migrations(db_path)
                cleaner = Cleaner(adoptants_file_path)
                db_connector.save_dataframe_to_table(cleaner.df, "adoption_analysis", db_path)
            st.success("Procesamiento completado!")

if __name__ == "__main__":
    main()