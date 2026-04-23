import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="LLM Readability Auditor", layout="wide")

st.title("🧠 LLM Readability Audit Dashboard")
st.write("Audit de lisibilité des sites pour IA / SEO / LLM (version cabinet de conseil)")

url = st.text_input("🔗 URL à analyser")


def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    return r.text


def analyze(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(separator=" ")
    words = len(text.split())

    scripts = len(soup.find_all("script"))
    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))
    links = len(soup.find_all("a"))

    title = soup.title.text if soup.title else "Missing"

    js_heavy = scripts > 20
    low_content = words < 300
    good_structure = (h1 >= 1 and h2 >= 2)

    score = 100
    if js_heavy:
        score -= 25
    if low_content:
        score -= 25
    if not good_structure:
        score -= 20
    if title == "Missing":
        score -= 10
    if words < 100:
        score -= 20

    score = max(0, score)

    return {
        "title": title,
        "words": words,
        "scripts": scripts,
        "h1": h1,
        "h2": h2,
        "links": links,
        "score": score,
        "js_heavy": js_heavy,
        "low_content": low_content,
        "good_structure": good_structure
    }


if url:
    try:
        result = analyze(url)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("⭐ Score LLM", f"{result['score']}/100")
        with col2:
            st.metric("🧾 Words", result['words'])
        with col3:
            st.metric("⚙️ Scripts", result['scripts'])

        st.subheader("📊 Diagnostic")

        if result["js_heavy"]:
            st.warning("Site fortement dépendant du JavaScript")
        else:
            st.success("Dépendance JavaScript raisonnable")

        if result["low_content"]:
            st.warning("Faible densité de contenu lisible")
        else:
            st.success("Bonne densité de contenu")

        if result["good_structure"]:
            st.success("Structure HTML correcte (H1/H2)")
        else:
            st.warning("Structure HTML insuffisante")

        st.subheader("📄 Détails")
        st.json(result)

        st.subheader("🧠 Interprétation cabinet de conseil")

        if result["score"] >= 80:
            st.success("Site très bien optimisé pour LLM / SEO")
        elif result["score"] >= 50:
            st.warning("Site moyennement optimisé, améliorable")
        else:
            st.error("Site peu lisible pour IA / SEO faible")

    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {str(e)}")

else:
    st.info("Entre une URL pour lancer l'audit")
