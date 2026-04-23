import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd

st.set_page_config(page_title="LLM Readability Audit", layout="wide")

st.title("🧠 LLM Readability Audit Dashboard – Pro Cabinet Version")
st.write("Audit avancé + comparaison + plan d’actions pour optimisation SEO / LLM / UX")

url = st.text_input("🔗 URL principale à analyser")
url_comp = st.text_input("⚖️ URL de comparaison (optionnel)")


def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    return r.text


def analyze(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(separator=" ")
    words = len(text.split())

    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))
    h3 = len(soup.find_all("h3"))

    images = soup.find_all("img")
    img_count = len(images)
    missing_alt = len([img for img in images if not img.get("alt")])

    scripts = soup.find_all("script")
    script_count = len(scripts)

    title = soup.title.text.strip() if soup.title else None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_present = meta_desc is not None

    is_spa_like = words < 80 and script_count > 10

    score = 100

    issues = []

    if script_count > 25:
        score -= 20
        issues.append("Forte dépendance JavaScript")

    if words < 300:
        score -= 20
        issues.append("Faible contenu texte exploitable")

    if h1 == 0:
        score -= 15
        issues.append("Absence de H1")

    if h2 < 2:
        score -= 10
        issues.append("Structure H2 insuffisante")

    if missing_alt > 0:
        score -= 10
        issues.append(f"{missing_alt} images sans alt")

    if not meta_desc_present:
        score -= 10
        issues.append("Meta description manquante")

    if is_spa_like:
        score -= 15
        issues.append("Site SPA-like (contenu injecté JS)")

    score = max(0, score)

    return {
        "url": url,
        "score": score,
        "words": words,
        "h1": h1,
        "h2": h2,
        "h3": h3,
        "images": img_count,
        "missing_alt": missing_alt,
        "scripts": script_count,
        "title": title,
        "meta_description": meta_desc_present,
        "issues": issues
    }


def generate_actions(result):
    actions = []

    if result["script_count"] > 25:
        actions.append("Réduire dépendance JavaScript ou passer en SSR (Next.js)")

    if result["words"] < 300:
        actions.append("Ajouter du contenu HTML statique (textes SEO visibles)")

    if result["h1"] == 0:
        actions.append("Ajouter un H1 unique par page")

    if result["h2"] < 2:
        actions.append("Structurer contenu avec H2 (sections claires)")

    if result["missing_alt"] > 0:
        actions.append("Ajouter attribut alt sur toutes les images")

    if not result["meta_description"]:
        actions.append("Ajouter meta description optimisée SEO")

    if "SPA-like" in " ".join(result["issues"]):
        actions.append("Passer en rendu serveur (SSR) pour lisibilité LLM")

    return actions


if url:
    try:
        main = analyze(url)

        st.subheader("📊 Score principal")
        st.metric("Score LLM / SEO", f"{main['score']}/100")

        col1, col2, col3 = st.columns(3)
        col1.metric("Mots", main["words"])
        col2.metric("Scripts", main["scripts"])
        col3.metric("Images", main["images"])

        st.subheader("⚠️ Problèmes détectés")
        for i in main["issues"]:
            st.warning(i)

        st.subheader("🛠 Actions recommandées (priorisées)")
        actions = generate_actions(main)
        for a in actions:
            st.success(a)

        # COMPARAISON
        if url_comp:
            st.subheader("⚖️ Comparaison")
            comp = analyze(url_comp)

            df = pd.DataFrame([
                {"Site": "Principal", "Score": main["score"]},
                {"Site": "Comparé", "Score": comp["score"]}
            ])

            st.bar_chart(df.set_index("Site"))

            st.write("### Détail comparaison")
            st.json({"principal": main, "comparé": comp})

            diff = main["score"] - comp["score"]
            st.metric("Écart de performance", diff)

    except Exception as e:
        st.error(f"Erreur : {str(e)}")
else:
    st.info("Entre une URL pour lancer l'audit")
