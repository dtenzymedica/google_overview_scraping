import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from fuzzywuzzy import fuzz
import spacy

# Loading the Spacy Languages
nlp_models = {
    "US": spacy.load("en_core_web_sm"),
    "ES": spacy.load('es_core_news_sm'),
    "GE": spacy.load('de_core_news_sm'),
    "FR": spacy.load("fr_core_news_sm"),
    "IT": spacy.load('it_core_news_sm')
}

def preprocess_text(text, market):
    """
    Preprocess the text using language-specific spaCy models for lemmatization and stop-word removal.
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    doc = nlp_models[market](text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(set(tokens))  # Remove duplicates

def fuzzy_match(keyword, patterns, fuzzy_threshold=82):
    """
    Match a keyword to a list of patterns using both regex and fuzzy matching.
    """
    for pattern in patterns:
        # Check for exact regex match
        if re.search(pattern, keyword.lower()):
            return True
        # Check for fuzzy match
        if fuzz.partial_ratio(keyword.lower(), pattern.lower()) >= fuzzy_threshold:
            return True
    return False

def is_branded(keyword, branded_patterns, fuzzy_threshold=82):
    return fuzzy_match(keyword, branded_patterns, fuzzy_threshold)

def is_competitor(keyword, competitor_patterns, fuzzy_threshold=82):
    return fuzzy_match(keyword, competitor_patterns, fuzzy_threshold)

# Patterns for Each Country
patterns = {
    "US": {
        "branded": [
        r"\benzymedica\b", r"\bdigest gold\b", r"\bacid soothe\b", r"\bglutenease\b", r"\brepair gold\b",
        r"\bbean assist\b", r"\blypo gold\b", r"\bdigest spectrum\b", r"\baqua biome\b", r"\baquabiome omega 3\b",
        r"\bmagnesium mind\b", r"\bheart burn soothe\b", r"\bkids digest\b", r"\blipo\b", r"\bmagnesium motion\b",
        r"\bberberine phytosome\b", r"\bcandidase\b", r"\bdigest basic\b", r"\bglutease\b", r"\bveggiegest\b", r"\bserra\b",
        r"\benzymedica\s\w+\b", r"\bdairy assist\b", r"\bdairy assit\b"
        ],
        "competitor": [
            r"beano", r"zenwise", r"pure encapsulations", r"digestive advantage", 
            r"atrantil", r"thorne", r"now", r"enzyme science", r"metagenics", r"dr\. formulated", r"candida",
            r"zenwise\s\w+", r"beano\s\w+"
        ]
    },
    "ES": {
    "branded": [
        r"enzymedica", r"oro digestivo", r"calma ácida", r"glutenease", r"oro reparador",
        r"asistencia de frijoles", r"oro lipo", r"espectro digestivo", r"bioma acuático", r"aquabiome omega 3",
        r"mente magnesio", r"alivio de ardor de estómago", r"niños digestivos", r"lipo", r"movimiento magnesio",
        r"fitozoma de berberina", r"candidase", r"básico digestivo", r"glutease", r"veggiegest", r"serra", r"digest basic",
        r"digest gold", r"digest complete", r"digest spectrum", r"lypo gold", r"beanassist",
        r"enzymedica\s\w+", r"digestivo\s\w+"
    ],
    "competitor": [
        r"aerored gases", r"aerored gases forte vientre plano", r"allergy calm boiron", 
        r"aquilea gases forte", r"aquilea gases vientre plano", r"creon 25000 pancreatina", 
        r"daofood plus", r"enzymatic therapy gluten defense", r"fodzyme", r"gluten cutter", 
        r"now super enzymes", r"super enzymes kal", r"vegan digestive enzymes solgar", 
        r"viridian digestive aid", r"now"
    ]
},
"GE": {
    "branded": [
        r"enzymedica", r"digest gold", r"acid soothe", r"glutenease", r"repair gold",
        r"bean assist", r"lypo gold", r"digest spectrum", r"aqua biome", r"aquabiome omega 3",
        r"magnesium mind", r"heartburn relief", r"kids digest", r"lipo", r"magnesium motion",
        r"candidase", r"digest basic", r"glutease", r"veggiegest", r"serra",
        r"digest enzymes", r"digestive enzyme", r"verdauungsenzyme",
        r"enzymedica\s\w+", r"digest\s\w+", r"lypo\s\w+", r"glutenease\s\w+"
    ],
    "competitor": [
        r"beano", r"zenwise", r"pure encapsulations", r"digestive advantage",
        r"atrantil", r"thorne", r"now", r"enzyme science", r"metagenics", r"dr\. formulated",
        r"simeticon", r"source naturals", r"life extensions", r"nortase enzyme", 
        r"papaya enzym kapseln", r"velgastin", r"her one digestion boost", r"fiber plus magnesium",
        r"gluten block", r"gluten stop", r"gluten kapseln", r"gluten tabletten", r"rocky mountain enzym",
        r"esn verdauungsenzyme", r"senna tabletten", r"essential enzymes", r"probiotic 200 billion"
    ]
},
"IT": {
    "branded": [
        r"enzymedica", r"digest gold", r"gluten ease", r"lypo gold", r"glutenease",
        r"digest spectrum", r"enzymedica digest", r"digest basic", r"enzymedica probiotic",
        r"enzymedical9 glutenease", r"lypogold enzymedica", r"digest enzymes", r"enzimi digestivi enzymedica",
        r"enzymedica\s\w+", r"digest\s\w+", r"lypo\s\w+", r"glutenease\s\w+", r"enzimi caseina", r"enzimi per lattosio e glutine"
    ],
    "competitor": [
        r"beano", r"solgar", r"pure encapsulations", r"digestive advantage", r"helpzymes", r"erbenzym digest solgar",
        r"herbenzym digest solgar", r"provida enzimi", r"integratori enzimi con amilasi lipasi proteasi",
        r"prolife", r"nutraceutico enzimi digestivi", r"xls medical pro 7", r"enzimi digestivi ultra pure encapsulations",
        r"farmaci per celiaci", r"ozempic per dimagrire", r"liraglutide per dimagrire", r"pancreatina", r"pasti sostitutivi dimagranti",
        r"pasta senza glutine offerte", r"integratori brucia grassi addominali", r"prodotti gluten free e senza lattosio", r"gluten"
    ]
},
"FR": {
    "branded": [
        r"enzymedica", r"digest gold", r"gluten ease", r"lypo gold", r"glutenease",
        r"digest spectrum", r"kids digest", r"enzymes digestives bio", r"enzymes digestives gluten lactose",
        r"digest basic", r"enzymes digestives lipase", r"digest enzymes", r"enzymes pour digérer la caséine", r"enzyme gluten lactose", r"enzymedica\s\w+", r"digest\s\w+",
        r"lypo\s\w+", r"glutenease\s\w+"
    ],
    "competitor": [
         r"beano", r"candida", r"candidase", r"nutra digest", r"nutri&co", r"fenouil gélules",
        r"solgar", r"dr raphael perez", r"enzyme digestive vegan", r"enzyme digestive contre les gaz",
        r"gluteostop", r"gluterase", r"enzymes alpha-galactosidase", r"enzymes betaine",
        r"chewing pour estomac", r"pepsine", r"enzyme diet", r"enzyme digestive gluten"
    ]
},
}

file_path = "C:\google_scraping\Data\Copy of Enzymedica - Keyword Clustering & Relevancy Definition.xlsx"
# Load all sheets from the Excel file
all_sheets = pd.read_excel(file_path, sheet_name=None)

# Define the number of clusters
n_clusters = 3
clustered_data = {}

# Process each sheet
for sheet_name, sheet_data in all_sheets.items():
    sheet_data = pd.DataFrame(sheet_data)

    if "Keywords" not in sheet_data.columns:
        print(f"Skipping sheet '{sheet_name}' - 'Keywords' column missing")
        continue

    # Identify the market based on the sheet name
    market = "US"  
    if "ES" in sheet_name:
        market = "ES"
    elif "GE" in sheet_name:
        market = "GE"
    elif "IT" in sheet_name:
        market = "IT"
    elif "FR" in sheet_name:
        market = "FR"

    # Preprocess keywords for the identified market
    keywords = sheet_data["Keywords"].dropna().astype(str)
    preprocessed_keywords = keywords.apply(lambda text: preprocess_text(text, market))

    # Vectorize the preprocessed keywords using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(preprocessed_keywords)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)

    # Assign clusters and map them to categories using fuzzy matching
    sheet_data["MARKET"] = market
    sheet_data["KW Type"] = [
        "BR" if is_branded(keyword, patterns[market]["branded"]) 
        else ("CO" if is_competitor(keyword, patterns[market]["competitor"]) 
              else "GE")
        for keyword in keywords
    ]

    # Retain only relevant columns
    relevant_columns = ["MARKET", "Keywords", "KW Type"]
    sheet_data = sheet_data[relevant_columns]

    # Store processed data
    clustered_data[sheet_name] = sheet_data

# Save all processed data to a consolidated Excel file
output_path = "clustered_keywords.xlsx"
with pd.ExcelWriter(output_path) as writer:
    for sheet_name, data in clustered_data.items():
        data.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Cleaned and clustered keywords saved to {output_path}")
