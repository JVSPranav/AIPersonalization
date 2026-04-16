import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_website_text(url):
    """Scrapes the main text from a given URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else "No Title"
        h1 = [h.text.strip() for h in soup.find_all('h1')]
        paragraphs = [p.text.strip() for p in soup.find_all('p')][:5]
        
        return f"Title: {title}\nMain Headlines: {h1}\nSummary: {paragraphs}"
    except Exception as e:
        return f"Error reading website: {e}"

def generate_personalized_copy(ad_text, website_context):
    """Sends the Ad and Website data to the AI to get CRO-optimized updates."""
    prompt = f"""
    You are an expert Conversion Rate Optimization (CRO) copywriter.
    I have an ad creative and the current text of a landing page. 
    
    Ad Creative Description/Text:
    "{ad_text}"
    
    Current Landing Page Context:
    "{website_context}"
    
    Task: Write personalized elements for the landing page so it matches the promise and tone of the Ad Creative.
    Provide ONLY the following format:
    
    New Hero Headline: [Your headline here]
    New Sub-headline: [Your sub-headline here]
    New Call to Action (CTA) Button: [Your CTA here]
    Why this works (CRO principle): [Brief 1-sentence explanation]
    """
    
    response = model.generate_content(prompt)
    return response.text

st.set_page_config(page_title="Landing Page Personalizer", layout="centered")

st.title("Ad to Landing Page Personalizer")
st.write("Input an ad creative and a landing page URL to get a personalized, CRO optimized version.")

ad_input = st.text_area("1. Paste the Ad Creative text or description:", placeholder="e.g., 'Get 50% off our new AI running shoes.'")
url_input = st.text_input("2. Paste the Landing Page URL:", placeholder="https://example.com")

if st.button("Generate Personalized Page"):
    if not ad_input or not url_input:
        st.warning("Please provide both the Ad Creative and the URL.")
    else:
        with st.spinner("Analyzing website and generating CRO updates..."):
            site_context = get_website_text(url_input)

            if "Error" not in site_context:
                ai_suggestions = generate_personalized_copy(ad_input, site_context)
                
                st.success("Analysis Complete")
                st.subheader("Personalized Landing Page Elements")
                st.info(ai_suggestions)
                
                st.markdown("---")
                st.write("*Note: To prevent broken UI and layout shifts, this system dynamically suggests the text node replacements (Headlines, Sub-headlines, CTAs) rather than rewriting the site's raw HTML.*")
            else:
                st.error(site_context)