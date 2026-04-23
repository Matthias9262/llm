import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urlparse

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="LLM Readability Audit Pro", layout="wide")

st.title("🧠 LLM Readability Audit – Enterprise / Cabinet Version")
st.write("Analyse ultra détaillée SEO + LLM + UX + architecture web")

url = st.text_input("🔗 URL principale à analyser")
url_comp = st.text_input("⚖️ URL comparaison (optionnel)")

# ==============================
# FETCH HTML
# ==============================
def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except Exception as e:
        return ""

# ==============================
# CORE ANALYSIS
# ==============================
def analyze(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(separator=" ")
    words = len(text.split())

    # HEADINGS
    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))
    h3 = len(soup.find_all("h3"))

    # LINKS
    links = soup.find_all("a")
    link_count = len(links)

    # IMAGES
    images = soup.find_all("img")
    img_count = len(images)
    missing_alt = len([img for img in images if not img.get("alt")])

    # SCRIPTS
    scripts = soup.find_all("script")
    script_count = len(scripts)
    external_scripts = len([s for s in scripts if s.get("src")])

    # META
    title = soup.title.text.strip() if soup.title else None
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_present = meta_desc is not None

    # BODY QUALITY
    body_text = soup.body.get_text(" ") if soup.body else ""
    body_words = len(body_text.split())

    # SEO SIGNALS
    canonical = soup.find("link", rel="canonical")
    canonical_ok = canonical is not None

    lang = soup.html.get("lang") if soup.html else None

    # SPA HEURISTIC
    is_spa = words < 80 and script_count > 10

    # READABILITY
    avg_sentence_length = words / max(len(re.split(r'[.!?]', text)), 1)

    # SCORE INIT
    score = 100
    issues = []

    # ==============================
    # SCORING LOGIC
    # ==============================

    if script_count > 30:
        score -= 20
        issues.append("Trop de JavaScript (risque SPA / rendu client lourd)")

    if words < 300:
        score -= 20
        issues.append("Contenu texte insuffisant pour SEO / LLM")

    if h1 == 0:
        score -= 15
        issues.append("Absence de H1 (structure critique)")

    if h2 < 2:
        score -= 10
        issues.append("Structure H2 insuffisante")

    if missing_alt > 0:
        score -= 10
        issues.append("Images sans attribut ALT (SEO + accessibilité)")

    if not meta_desc_present:
        score -= 10
        issues.append("Meta description absente")

    if not canonical_ok:
        score -= 5
        issues.append("Canonical manquant")

    if not lang:
        score -= 5
        issues.append("Langue HTML non définie")

    if is_spa:
        score -= 15
        issues.append("Site SPA-like (contenu dépend JS)")

    if avg_sentence_length > 25:
        score -= 5
        issues.append("Phrases trop longues (lisibilité faible)")

    score = max(0, score)

    return {
        "url": url,
        "score": score,
        "words": words,
        "body_words": body_words,
        "h1": h1,
        "h2": h2,
        "h3": h3,
        "links": link_count,
        "images": img_count,
        "missing_alt": missing_alt,
        "scripts": script_count,
        "external_scripts": external_scripts,
        "title": title,
        "meta_description": meta_desc_present,
        "canonical": canonical_ok,
        "lang": lang,
        "spa_like": is_spa,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "issues": issues
    }

# ==============================
# ACTION ENGINE
# ==============================
def generate_actions(r):
    actions = []

    if r["scripts"] > 30:
        actions.append("Réduire le JavaScript ou passer en SSR (Next.js / rendu serveur)")

    if r["words"] < 300:
        actions.append("Ajouter du contenu HTML statique riche (SEO + LLM)")

    if r["h1"] == 0:
        actions.append("Ajouter un H1 unique par page")

    if r["h2"] < 2:
        actions.append("Structurer le contenu avec des sections H2")

    if r["missing_alt"] > 0:
        actions.append("Ajouter des ALT sur toutes les images")

    if not r["meta_description"]:
        actions.append("Ajouter meta description optimisée SEO")

    if not r["canonical"]:
        actions.append("Ajouter balise canonical")

    if not r["lang"]:
        actions.append("Définir la langue HTML (lang attribute)")

    if r["spa_like"]:
        actions.append("Passer en architecture SSR pour lisibilité IA")

    if r["avg_sentence_length"] > 25:
        actions.append("Réduire longueur des phrases pour lisibilité")

    return actions

# ==============================
# DISPLAY
# ==============================
if url:
    try:
        main = analyze(url)

        st.subheader("📊 Score global")
        st.metric("LLM / SEO Score", f"{main['score']}/100")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mots", main["words"])
        col2.metric("Scripts", main["scripts"])
        col3.metric("Images", main["images"])
        col4.metric("Liens", main["links"])

        st.subheader("⚠️ Problèmes détectés")
        for i in main["issues"]:
            st.warning(i)

        st.subheader("🛠 Actions correctives (priorisées)")
        for a in generate_actions(main):
            st.success(a)

        st.subheader("📌 Analyse technique complète")
        st.json(main)

        # ==============================
        # COMPARISON
        # ==============================
        if url_comp:
            comp = analyze(url_comp)

            st.subheader("⚖️ Comparaison des sites")

            df = pd.DataFrame([
                {"Site": "Principal", "Score": main["score"]},
                {"Site": "Comparé", "Score": comp["score"]}
            ])

            st.bar_chart(df.set_index("Site"))

            diff = main["score"] - comp["score"]
            st.metric("Écart de performance", diff)

            st.write("### Détails comparatif")
            st.json({"principal": main, "comparé": comp})

    except Exception as e:
        st.error(f"Erreur : {str(e)}")
else:
    st.info("Entre une URL pour lancer l’audit")
