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
USER_AGENT = "Mozilla/5.0"


# ==============================
# MODEL
# ==============================

def load_model():
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
    return pipe


# ==============================
# TEXT PROCESSING
# ==============================

def extract_text_from_html(html):
    for tag in html(["script", "style", "noscript"]):
        tag.extract()

    paragraphs = [p.get_text().strip() for p in html.find_all("p")]
    return " ".join(paragraphs)


def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


# ==============================
# WEB UTILITIES
# ==============================

def normalize_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    return url


def fetch_page(url):
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        return None

    return response.text


def get_domain(url):
    return urlparse(url).netloc


# ==============================
# AI ANALYSIS
# ==============================

def build_prompt(context):
    return f"""
You analyze webpage content.

Context:
{context}

Question:
Is this webpage related to robotics?

Answer ONLY True or False.
"""


def analyze_content(pipe, context):
    prompt = build_prompt(context)

    result = pipe(prompt, return_full_text=False)
    generated = result[0]["generated_text"].strip().lower()

    return generated


# ==============================
# PAGE ANALYSIS PIPELINE
# ==============================

def process_webpage(pipe, url, blocked_websites):

    url = normalize_url(url)
    domain = get_domain(url)

    if blocked_websites.get(domain):
        print("This website is blocked. Please try another one.")
        return

    page = fetch_page(url)

    if not page:
        print("Failed to access the website.")
        return

    html = BeautifulSoup(page, "html.parser")

    print("Extracting page content...")

    text = extract_text_from_html(html)

    if len(text) < MIN_TEXT_LENGTH:
        print("Could not extract useful text from the page.")
        return

    chunks = chunk_text(text)
    context = "\n".join(chunks[:5])

    print("Analyzing content...")

    generated = analyze_content(pipe, context)

    print("\nAnalysis Result:\n")

    if "false" in generated:
        print("The webpage is not related to robotics.")
        print("Blocking this website for future analysis.")
        blocked_websites[domain] = domain

    elif "true" in generated:
        print("The webpage is related to robotics.")

    else:
        print("Could not determine the result:", generated)


# ==============================
# UI
# ==============================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    print("1. Web Analysis")
    print("2. Video Analysis (Coming Soon)")
    print("0. Exit")


def wait():
    input("\nPress Enter to continue...")


# ==============================
# MAIN
# ==============================

def main():

    pipe = load_model()

    print("Loading blocked websites list...")
    blocked_websites = {}
    print("Blocked websites list loaded successfully!")

    while True:

        clear_screen()
        show_menu()

        option = input("\nSelect an option: ")

        if option == "1":

            url = input("\nEnter the URL: ")

            try:
                process_webpage(pipe, url, blocked_websites)
            except Exception as e:
                print("Error:", e)

            wait()

        elif option == "2":

            print("Video Analysis is coming soon!")
            wait()

        elif option == "0":

            print("Exiting...")
            break

        else:

            print("Invalid option. Please try again.")
            wait()


if __name__ == "__main__":
    main()