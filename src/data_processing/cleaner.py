import pandas as pd
import re
from src.utils.db_connector import save_dataframe_to_table

class Cleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = self.load_file()
        self.clean()

    def load_file(self):
        if self.filepath.endswith(".csv"):
            return pd.read_csv(self.filepath)
        elif self.filepath.endswith((".xlsx", ".xls")):
            return pd.read_excel(self.filepath)
        elif self.filepath.endswith(".json"):
            return pd.read_json(self.filepath)
        else:
            raise ValueError("Formato no soportado")

    def normalize_column_names(self):
        self.df.columns = [
            re.sub(r"\s+", "_", col.strip().lower())
            for col in self.df.columns
        ]

    def clean_strings(self):
        self.df = self.df.apply(
            lambda col: col.str.strip().str.lower() if col.dtypes == 'object' else col
        )

    def standardize_na_values(self):
        na_values = {"NA", "N/A", "N\\A", "N.A.", "NONE", "na", "n/a", "none", ""}
        self.df.replace(na_values, "", inplace=True, regex=True)

    def standardize_dates(self):
        """Standardize date columns to ISO format (YYYY-MM-DD)."""
        for col in self.df.columns:
            if "fecha" in col: 
                self.df[col] = pd.to_datetime(
                    self.df[col], errors="coerce", dayfirst=True
                ).dt.strftime("%Y-%m-%d")
                self.df[col] = self.df[col].fillna("")

    def convert_numerics(self):
        """Convert specific numeric fields to integers, replacing invalid values with 0."""
        numeric_columns = ["edad", "cuantos", "integrantes_familia", "perros", "gatos"]
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0).astype(int)

    def rename_columns(self):
        """Rename columns to more descriptive names."""
        corrections = {
            "cas_o_depa": "tipo_vivienda",
            "genero": "genero_mascota",
            "género_adoptante": "genero_adoptante",
        }
        self.df.rename(columns=corrections, inplace=True)

    def clean(self):
        """Apply all cleaning steps."""
        self.normalize_column_names()
        self.rename_columns()
        self.standardize_na_values()
        self.clean_strings()
        self.standardize_dates()
        self.convert_numerics()

    def get_cleaned_data(self):
        return self.df

    def to_csv(self, output_path):
        self.df.to_csv(output_path, index=False)

    def to_json(self, output_path):
        self.df.to_json(output_path, orient="records", force_ascii=False, indent=2)

    def to_database(self, table_name, db_path):
        save_dataframe_to_table(self.df, table_name, db_path)
