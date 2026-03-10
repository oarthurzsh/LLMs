from transformers import pipeline
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse


# ==============================
# CONFIGURATION
# ==============================

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
CHUNK_SIZE = 128
MIN_TEXT_LENGTH = 50


# ==============================
# TEXT PROCESSING
# ==============================

def extract_text_from_html(html):
    for tag in html(["script", "style", "noscript"]):
        tag.extract()

    paragraphs = [p.get_text().strip() for p in html.find_all("p")]
    text = " ".join(paragraphs)

    return text


def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# ==============================
# MODEL LOADING
# ==============================

print("Loading model, please wait...")

pipe = pipeline(
    "text-generation",
    model=MODEL_ID,
    device_map="auto",
    temperature=0.1,
    max_length=None,
    max_new_tokens=5
)

print("Model loaded successfully!")


# ==============================
# BLOCKED WEBSITES
# ==============================

print("Loading blocked websites list...")

blocked_websites = {}

print("Blocked websites list loaded successfully!")


# ==============================
# MAIN LOOP
# ==============================

while True:

    os.system('cls' if os.name == 'nt' else 'clear')

    print("1. Web Analysis")
    print("2. Video Analysis (Coming Soon)")
    print("0. Exit")

    option = input("\nSelect an option: ")

    if option == "1":

        url = input("\nEnter the URL: ")
        domain = urlparse(url).netloc

        if blocked_websites.get(domain):
            print("This website is blocked. Please try another one.")
            input("\nPress Enter to continue...")
            continue

        try:

            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print("Failed to access the website.")
                input("\nPress Enter to continue...")
                continue

            html = BeautifulSoup(response.text, "html.parser")

            print("Extracting page content...")

            text = extract_text_from_html(html)

            if len(text) < MIN_TEXT_LENGTH:
                print("Could not extract useful text from the page.")
                input("\nPress Enter to continue...")
                continue

            chunks = chunk_text(text)
            context = "\n".join(chunks[:5])

            prompt = f"""
You analyze webpage content.

Context:
{context}

Question:
Is this webpage related to robotics?

Answer ONLY True or False.
"""

            print("Analyzing content...")

            result = pipe(prompt, return_full_text=False)
            generated = result[0]["generated_text"].strip().lower()

            print("\nAnalysis Result:\n")

            if "false" in generated:
                print("The webpage is not related to robotics.")
                print("Blocking this website for future analysis.")
                blocked_websites[domain] = domain

            elif "true" in generated:
                print("The webpage is related to robotics.")

            else:
                print("Could not determine the result:", generated)

        except Exception as e:
            print("Error:", e)

        input("\nPress Enter to continue...")

    elif option == "2":

        print("Video Analysis is coming soon!")
        input("\nPress Enter to continue...")

    elif option == "0":

        print("Exiting...")
        break

    else:

        print("Invalid option. Please try again.")
        input("\nPress Enter to continue...")