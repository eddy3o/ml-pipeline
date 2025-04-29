import json
import pandas as pd
import spacy
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from ollama import chat
import sqlite3

class AdoptionFairAnalyzer:
    def __init__(self, json_path):
        self.df = self.load_and_process_data(json_path)
        self.nlp = spacy.load("es_core_news_sm")
        self.setup_visuals()
        
    def setup_visuals(self):
        plt.style.use('ggplot')
        sns.set_palette("husl")
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['figure.dpi'] = 300

    def load_and_process_data(self, path):
        """Carga y procesa los datos con manejo de campos variables"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        df = pd.json_normalize(data, sep='_')
        
        # Normalización avanzada
        df['fecha_scraping'] = pd.to_datetime(df['fecha_scraping'])
        df['text'] = df['text'].str.replace(r'\s+', ' ', regex=True)
        df['text_clean'] = df['text'].str.lower().str.replace(r'[^\w\s]', '', regex=True)
        
        return df

    def extract_entities(self):
        """Extracción de entidades clave usando NLP"""
        # Lista de colonias o zonas específicas dentro de Morelia
        known_locations = [
            'altozano', 'el centro', 'chapultepec', 'las américas', 'vista bella', 
            'felicitas del río', 'prados verdes', 'la huerta', 'tres marías', 'punhuato'
        ]
        
        entities = []
        for doc in self.nlp.pipe(self.df['text_clean'], batch_size=50):
            record = {
                'fechas': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
                'lugares': [
                    ent.text for ent in doc.ents if ent.label_ == 'LOC' and any(loc in ent.text.lower() for loc in known_locations)
                ],
                'animales': list({ent.text for ent in doc.ents if ent.label_ == 'MISC' and any(x in ent.text.lower() for x in ['perro', 'gato', 'michi', 'lomito'])})
            }
            entities.append(record)
        
        return pd.json_normalize(entities).add_prefix('ent_')
    
    def generate_location_analysis(self):
        """Análisis profesional de ubicaciones con visualización"""
        location_data = self.df.join(self.extract_entities())
        
        # Conteo de menciones por lugar
        location_counts = pd.Series(
            [loc for sublist in location_data['ent_lugares'] for loc in sublist]
        ).value_counts().head(10)
        
        # Visualización
        plt.figure(figsize=(14, 8))
        ax = sns.barplot(x=location_counts.values, y=location_counts.index, palette="viridis")
        ax.set_title('Top 10 Lugares Mencionados en Ferias de Adopción', pad=20)
        ax.set_xlabel('Frecuencia de Mención')
        ax.set_ylabel('')
        plt.tight_layout()
        plt.savefig('top_lugares.png', transparent=True)
        plt.close()
        
        return location_counts

    def generate_temporal_analysis(self):
        """Análisis temporal profesional"""
        temp_df = self.df.copy()
        temp_df['mes'] = temp_df['fecha_scraping'].dt.to_period('M')
        
        timeline = temp_df.groupby('mes').size()
        
        plt.figure(figsize=(14, 6))
        timeline.plot(kind='line', marker='o', linewidth=2)
        plt.title('Actividad de Ferias por Mes', pad=15)
        plt.xlabel('Mes')
        plt.ylabel('Número de Eventos')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('linea_temporal.png')
        plt.close()
        
        return timeline
    
    def analyze_combined_data(self, adoptants_json_path):
        """Analiza datos combinados de ferias y adoptantes"""
        # Cargar datos de adoptantes
        with open(adoptants_json_path, 'r') as f:
            adoptants_data = json.load(f)
        
        adoptants_df = pd.DataFrame(adoptants_data)
        adoptants_df['domicilio_clean'] = adoptants_df['domicilio'].str.lower().str.replace(r'[^\w\s,]', '', regex=True)
        
        # Extraer zonas mencionadas en domicilios
        adoptants_df['zones'] = adoptants_df['domicilio_clean'].apply(
            lambda x: [loc for loc in self.extract_known_locations() if loc in x]
        )
        
        # Extraer ubicaciones de ferias
        self.extract_entities()
        fair_locations = [loc for sublist in self.df['ent_lugares'] for loc in sublist]
        
        # Combinar ubicaciones de ferias y domicilios
        adoptant_locations = [zone for zones in adoptants_df['zones'] for zone in zones]
        combined_locations = fair_locations + adoptant_locations
        
        # Conteo de menciones por zona
        location_counts = pd.Series(combined_locations).value_counts()
        
        # Visualización
        plt.figure(figsize=(14, 8))
        sns.barplot(x=location_counts.values, y=location_counts.index, palette="viridis")
        plt.title('Zonas Mencionadas en Ferias y Domicilios', pad=20)
        plt.xlabel('Frecuencia de Mención')
        plt.ylabel('Zonas')
        plt.tight_layout()
        plt.savefig('combined_zones.png', transparent=True)
        plt.close()
        
        return location_counts

    def extract_known_locations(self):
        """Devuelve la lista de colonias o zonas específicas dentro de Morelia"""
        return [
            'altozano', 'el centro', 'chapultepec', 'las américas', 'vista bella', 
            'felicitas del río', 'prados verdes', 'la huerta', 'tres marías', 'punhuato',
            'punta del este', 'punta monarca'
        ]

    def generate_ai_insights(self):
        """Generación de insights con modelo LLM usando datos procesados"""
        context = {
            'top_lugares': self.generate_location_analysis().head(5).to_dict(),
            'temporal_data': {str(k): v for k, v in self.generate_temporal_analysis().to_dict().items()},
            'animal_counts': self.df['text_clean'].str.contains('perro|gato').value_counts().to_dict()
        }
        
        prompt = f"""Como experto en análisis de datos de adopción animal, genera un reporte profesional en español con:

1. **Tendencias principales** (lugares y temporalidad)
2. **Recomendaciones estratégicas** basadas en los datos
3. **Insights clave** para mejorar las adopciones

Datos clave:
{json.dumps(context, indent=2)}

Formato requerido:
- Encabezado con título
- Secciones claras con viñetas
- Conclusiones finales destacadas

Longitud requerida: 
- Al rededor de 1000 palabras.

Consideraciones: 
- Todas los datos son de la ciudad de Morelia, Michoacán, localiza tendencias específicas en la región.
- Usa un lenguaje claro y profesional.
- Ten en cuenta la temporalidad y los lugares más mencionados.
- Haz una tabla con: Temporalidad, lugares y frecuencia de adopciones.
- Analiza la frecuencia de adopciones de perros y gatos.
- Usa un tono profesional y directo.
- No incluyas información innecesaria o redundante.
- Investiga patrones de comportamiento en la adopción de mascotas. Ademas, considera la influencia de eventos locales y ferias de adopción en la comunidad.
- Analiza la relación entre la temporalidad y la adopción de perros y gatos, considerando factores como la estacionalidad y eventos locales.
- Menciona la importancia de la promoción de adopciones y el impacto de las ferias en la comunidad, ademas de mencionar las estrategias de marketing y comunicación utilizadas para fomentar la adopción de mascotas, asi como organizaciones locales que apoyan estas iniciativas.
"""

        response = chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        
        print("\n📊 **Reporte Analítico Generado por IA**\n")
        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)

    def generate_word_cloud(self):
        """Word cloud profesional con parámetros optimizados"""
        text = ' '.join(self.df['text_clean'].dropna())
        
        wordcloud = WordCloud(
            width=1600,
            height=900,
            background_color='white',
            colormap='viridis',
            max_words=150,
            stopwords={'que', 'los', 'las', 'del', 'para'}
        ).generate(text)
        
        plt.figure(figsize=(18, 12))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Palabras Clave en Descripciones de Ferias', pad=20, fontsize=18)
        plt.savefig('wordcloud.png', bbox_inches='tight')
        plt.close()


class CombinedAnalyzer:
    def __init__(self, fairs_json_path, adoptants_json_path):
        self.fairs_df = self.load_fairs_data(fairs_json_path)
        self.adoptants_df = self.load_adoptants_data(adoptants_json_path)
        self.nlp = spacy.load("es_core_news_sm")
        self.known_locations = [
            'altozano', 'el centro', 'chapultepec', 'las américas', 'vista bella', 
            'felicitas del río', 'prados verdes', 'la huerta', 'tres marías', 'punhuato',
            'punta del este', 'punta monarca'
        ]
    
    def load_fairs_data(self, path):
        """Carga y procesa los datos de ferias"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        df = pd.json_normalize(data, sep='_')
        df['text_clean'] = df['text'].str.lower().str.replace(r'[^\w\s]', '', regex=True)
        return df

    def load_adoptants_data(self, path):
        """Carga y procesa los datos de adoptantes"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        df['domicilio_clean'] = df['domicilio'].str.lower().str.replace(r'[^\w\s,]', '', regex=True)
        return df

    def extract_fair_locations(self):
        """Extrae las ubicaciones mencionadas en los textos de las ferias"""
        entities = []
        for doc in self.nlp.pipe(self.fairs_df['text_clean'], batch_size=50):
            locations = [
                ent.text for ent in doc.ents if ent.label_ == 'LOC' and any(loc in ent.text.lower() for loc in self.known_locations)
            ]
            entities.append(locations)
        
        self.fairs_df['extracted_locations'] = entities

    def analyze_combined_locations(self):
        """Analiza las zonas mencionadas en ferias y domicilios"""
        # Extraer ubicaciones de ferias
        self.extract_fair_locations()
        fair_locations = [loc for sublist in self.fairs_df['extracted_locations'] for loc in sublist]
        
        # Extraer ubicaciones de domicilios
        self.adoptants_df['zones'] = self.adoptants_df['domicilio_clean'].apply(
            lambda x: [loc for loc in self.known_locations if loc in x]
        )
        adoptant_locations = [zone for zones in self.adoptants_df['zones'] for zone in zones]
        
        # Combinar y contar menciones
        combined_locations = fair_locations + adoptant_locations
        location_counts = pd.Series(combined_locations).value_counts()
        
        # Visualización
        plt.figure(figsize=(14, 8))
        sns.barplot(x=location_counts.values, y=location_counts.index, palette="viridis")
        plt.title('Zonas Mencionadas en Ferias y Domicilios', pad=20)
        plt.xlabel('Frecuencia de Mención')
        plt.ylabel('Zonas')
        plt.tight_layout()
        plt.savefig('combined_zones.png', transparent=True)
        plt.close()
        
        return location_counts

def load_fairs_data(json_path):
    """Carga los datos de ferias en la base de datos."""
    conn = sqlite3.connect('adoption_analysis.db')
    cursor = conn.cursor()
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    for record in data:
        text = record.get('text', None)
        fecha_scraping = record.get('fecha_scraping', None)
        cursor.execute('''
            INSERT INTO fairs (text, fecha_scraping)
            VALUES (?, ?)
        ''', (text, fecha_scraping))
    
    conn.commit()
    conn.close()
    print("Datos de ferias cargados con éxito.")

def load_adoptants_data(json_path):
    """Carga los datos de adoptantes en la base de datos."""
    conn = sqlite3.connect('adoption_analysis.db')
    cursor = conn.cursor()
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    for record in data:
        cursor.execute('''
            INSERT INTO adoptants (
                fecha, buen_adoptante, genero, interes, genero_adoptante, edad,
                domicilio, cas_o_depa, integrantes_familia, perros, gatos, otro,
                cachorro_previo, cuantos, motivo, razon_de_rechazo, razon_aceptacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('fecha'),
            record.get('buen adoptante'),
            record.get('genero'),
            record.get('interes'),
            record.get('género adoptante'),
            record.get('edad'),
            record.get('domicilio'),
            record.get('cas o depa'),
            record.get('integrantes familia'),
            record.get('perros'),
            record.get('gatos'),
            record.get('otro'),
            record.get('cachorro previo'),
            record.get('cuantos'),
            record.get('motivo'),
            record.get('razon de rechazo'),
            record.get('razon aceptacion')
        ))
    
    conn.commit()
    conn.close()
    print("Datos de adoptantes cargados con éxito.")

def analyze_combined_data_from_db():
    """Analiza los datos combinados de ferias y adoptantes desde la base de datos."""
    conn = sqlite3.connect('adoption_analysis.db')
    
    # Consultar datos de ferias
    fairs_df = pd.read_sql_query('SELECT * FROM fairs', conn)
    
    # Consultar datos de adoptantes
    adoptants_df = pd.read_sql_query('SELECT * FROM adoptants', conn)
    
    # Extraer zonas mencionadas en domicilios
    known_locations = [
        'altozano', 'el centro', 'chapultepec', 'las américas', 'vista bella', 
        'felicitas del río', 'prados verdes', 'la huerta', 'tres marías', 'punhuato'
    ]
    adoptants_df['zones'] = adoptants_df['domicilio'].str.lower().apply(
        lambda x: [loc for loc in known_locations if loc in x] if x else []
    )
    
    # Combinar ubicaciones de ferias y domicilios
    combined_locations = []
    for text in fairs_df['text']:
        if text:
            combined_locations.extend([loc for loc in known_locations if loc in text.lower()])
    for zones in adoptants_df['zones']:
        combined_locations.extend(zones)
    
    # Conteo de menciones por zona
    location_counts = pd.Series(combined_locations).value_counts()
    
    # Visualización
    plt.figure(figsize=(14, 8))
    sns.barplot(x=location_counts.values, y=location_counts.index, palette="viridis")
    plt.title('Zonas Mencionadas en Ferias y Domicilios', pad=20)
    plt.xlabel('Frecuencia de Mención')
    plt.ylabel('Zonas')
    plt.tight_layout()
    plt.savefig('combined_zones.png', transparent=True)
    plt.close()
    
    conn.close()
    return location_counts

# Cargar datos en la base de datos
load_fairs_data('ScrapeV1.Datos Investigacion.json')
load_adoptants_data('adoptantes.json')

# Uso del sistema
analyzer = CombinedAnalyzer(
    'ScrapeV1.Datos Investigacion.json',
    'adoptantes.json'
)
combined_analysis = analyzer.analyze_combined_locations()
print(combined_analysis)

# Ejecutar análisis desde la base de datos
result = analyze_combined_data_from_db()
print(result)

# Uso del sistema
analyzer = AdoptionFairAnalyzer('ScrapeV1.Datos Investigacion.json')
analyzer.generate_location_analysis()
analyzer.generate_temporal_analysis()
analyzer.generate_word_cloud()
analyzer.generate_ai_insights()

# Análisis combinado con datos de adoptantes
combined_analysis = analyzer.analyze_combined_data('adoptantes.json')
print(combined_analysis)