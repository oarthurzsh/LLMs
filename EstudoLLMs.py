from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse


# ==============================
# CONFIG
# ==============================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MIN_TEXT_LENGTH = 50

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded!")

# ==============================
# CLASS DEFINITIONS
# ==============================

class_examples = {
    "True": [
        "educational robotics projects for students",
        "how to build a robot using arduino tutorial",
        "lego mindstorms robotics activity for classroom",
        "teaching robotics with sensors and programming",
        "robotics education lesson plan"
    ],

    "Robótica": [
        "industrial robotics automation systems",
        "robotics engineering research",
        "robotics industry news",
        "AI robotics development",
        "commercial robotics products"
    ],

    "False": [
        "mathematics learning activities",
        "physics lessons for students",
        "history educational resources",
        "how to apply to university",
        "biology teaching materials"
    ]
}

# ==============================
# CREATE CLASS EMBEDDINGS
# ==============================

class_embeddings = {}

for label, texts in class_examples.items():
    emb = model.encode(texts)
    class_embeddings[label] = emb.mean(axis=0)


# ==============================
# TEXT EXTRACTION
# ==============================

def extract_text_from_html(html):

    for tag in html(["script", "style", "noscript"]):
        tag.extract()

    paragraphs = [p.get_text().strip() for p in html.find_all("p")]

    return " ".join(paragraphs)


# ==============================
# CLASSIFICATION
# ==============================

def classify_text(text):

    emb = model.encode([text])[0]

    scores = {}

    for label, class_emb in class_embeddings.items():
        score = cosine_similarity([emb], [class_emb])[0][0]
        scores[label] = score

    return max(scores, key=scores.get)


# ==============================
# BLOCKED WEBSITES
# ==============================

blocked_websites = {}


# ==============================
# MAIN LOOP
# ==============================

while True:

    os.system('cls' if os.name == 'nt' else 'clear')

    print("1. Web Analysis")
    print("0. Exit")

    option = input("\nSelect an option: ")

    if option == "1":

        url = input("\nEnter the URL: ")
        domain = urlparse(url).netloc

        if blocked_websites.get(domain):
            print("This website is blocked.")
            input("\nPress Enter...")
            continue

        try:

            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print("Failed to access the website.")
                input("\nPress Enter...")
                continue

            html = BeautifulSoup(response.text, "html.parser")

            print("Extracting content...")

            text = extract_text_from_html(html)

            if len(text) < MIN_TEXT_LENGTH:
                print("Not enough useful text.")
                input("\nPress Enter...")
                continue

            text = text[:2000]

            print("Analyzing content...")

            result = classify_text(text)

            print("\nAnalysis Result:\n")

            if result == "False":
                print("The webpage is not related to robotics.")
                print("Blocking this website.")
                blocked_websites[domain] = domain

            elif result == "True":
                print("Educational robotics detected.")

            else:
                print("General robotics content detected.")

        except Exception as e:
            print("Error:", e)

        input("\nPress Enter...")

    elif option == "0":
        break