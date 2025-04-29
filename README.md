** Structure **

adopciones_ml/
│
├── data/
│   ├── raw/                  # Datos crudos (CSV, JSON, Excel de formularios/ferias)
│   ├── processed/            # Datos limpios y normalizados
│   └── models/               # Modelos serializados (.pkl, .joblib)
│
├── notebooks/                # Jupyter Notebooks para EDA y reportes
│   ├── 01_EDA.ipynb          # Análisis exploratorio
│   └── 02_Model_Evaluation.ipynb  
│
├── src/
│   ├── data_collection/      # Módulo de recolección
│   │   ├── scraper.py        # Web Scraping
│   │   └── forms_parser.py   # Procesamiento de formularios
│   │
│   ├── data_processing/      # Limpieza y transformación
│   │   ├── cleaner.py        # Normalización de datos
│   │   └── feature_engineer.py
│   │
│   ├── nlp/                 # Análisis de texto
│   │   ├── text_analyzer.py  # spaCy/NLTK
│   │   └── ollama_integration.py 
│   │
│   ├── modeling/            # Modelo predictivo
│   │   ├── train_model.py
│   │   └── evaluate.py      # Métricas y gráficos
│   │
│   └── utils/               # Funciones auxiliares
│       ├── db_connector.py   # Conexión a SQLite
│       └── config.py         # Parámetros globales
│
├── docs/                    # Documentación
│   ├── requirements.txt      # Dependencias
│   └── setup_instructions.md
│
├── .gitignore
├── main.py                  # Punto de entrada del flujo
└── README.md