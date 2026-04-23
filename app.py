import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="LLM Audit Pro", layout="wide")

st.title("🧠 LLM Readability Audit – Cabinet Version Pro")
st.write("Audit SEO / LLM / UX + analyse détaillée + ROI + comparaison")

urls_input = st.text_area("🔗 URLs (une par ligne)")

# =============================
# FETCH
# =============================
def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except:
        return ""

# =============================
# FRAMEWORK DETECTION
# =============================
def detect_framework(html):
    h = html.lower()
    if "next" in h or "__next" in h:
        return "Next.js (SSR React)"
    if "react" in h:
        return "React SPA"
    if "vue" in h:
        return "Vue.js"
    if "angular" in h:
        return "Angular"
    return "Server-rendered / Unknown"

# =============================
# DETAILED ANALYSIS
# =============================
def analyze(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(" ")
    words = len(text.split())

    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")

    imgs = soup.find_all("img")
    missing_alt = [i for i in imgs if not i.get("alt")]

    scripts = soup.find_all("script")

    title = soup.title.text if soup.title else None
    meta = soup.find("meta", attrs={"name": "description"})

    framework = detect_framework(html)

    issues = []
    actions = []

    # SCORES
    seo = 100
    content = 100
    tech = 100
    ux = 100

    # =============================
    # SEO ANALYSIS
    # =============================
    if not title:
        seo -= 15
        issues.append("❌ Title manquant")
        actions.append("Ajouter une balise <title> unique et descriptive")

    if len(h1) == 0:
        seo -= 20
        issues.append("❌ Aucun H1 détecté")
        actions.append("Ajouter un H1 unique par page")

    if len(h2) < 2:
        seo -= 10
        issues.append("⚠️ Structure H2 faible")
        actions.append("Structurer contenu avec H2 (sections claires)")

    if not meta:
        seo -= 10
        issues.append("⚠️ Meta description absente")
        actions.append("Ajouter meta description optimisée SEO")

    # =============================
    # CONTENT ANALYSIS
    # =============================
    if words < 300:
        content -= 25
        issues.append("❌ Contenu trop faible")
        actions.append("Ajouter du contenu textuel riche (FAQ, guides, pages)")

    sample_text = text[:400]

    # =============================
    # TECH ANALYSIS
    # =============================
    if len(scripts) > 30:
        tech -= 25
        issues.append("⚠️ Trop de JavaScript")
        actions.append("Réduire JS ou passer en SSR (Next.js)")

    # =============================
    # UX / ACCESSIBILITY
    # =============================
    if len(missing_alt) > 0:
        ux -= 20
        issues.append(f"❌ {len(missing_alt)} images sans ALT")
        actions.append("Ajouter attribut ALT sur toutes les images")

    # =============================
    # SPA DETECTION
    # =============================
    is_spa = words < 80 and len(scripts) > 10
    if is_spa:
        content -= 20
        issues.append("⚠️ Site SPA-like (contenu injecté JS)")
        actions.append("Passer en SSR pour rendre le contenu lisible IA/SEO")

    global_score = int((seo + content + tech + ux) / 4)

    return {
        "url": url,
        "framework": framework,
        "score": global_score,
        "seo": seo,
        "content": content,
        "tech": tech,
        "ux": ux,
        "words": words,
        "h1": len(h1),
        "h2": len(h2),
        "scripts": len(scripts),
        "missing_alt": len(missing_alt),
        "issues": issues,
        "actions": actions,
        "sample": sample_text
    }

# =============================
# ROI MODEL
# =============================
def roi(before, after):
    diff = after - before
    return {
        "traffic_gain_%": round(diff * 2.0, 2),
        "conversion_gain_%": round(diff * 0.7, 2),
        "revenue_impact_estimate_eur": round(diff * 150, 2)
    }

# =============================
# UI
# =============================
if urls_input:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    results = [analyze(u) for u in urls]

    df = pd.DataFrame([
        {
            "URL": r["url"],
            "Score": r["score"],
            "Framework": r["framework"]
        } for r in results
    ])

    st.subheader("📊 Comparaison globale")
    st.bar_chart(df.set_index("URL")["Score"])
    st.dataframe(df)

    best = max(results, key=lambda x: x["score"])
    worst = min(results, key=lambda x: x["score"])

    st.subheader("🏆 Insights")
    st.success(f"Meilleur site: {best['url']} ({best['score']})")
    st.error(f"Moins performant: {worst['url']} ({worst['score']})")

    st.subheader("💰 ROI estimé (optimisation potentielle)")
    st.write(roi(worst["score"], best["score"]))

    st.subheader("🔎 Analyse détaillée site par site")

    for r in results:
        st.markdown(f"---\n### {r['url']}")
        st.write(f"**Framework détecté :** {r['framework']}")
        st.write(f"**Score global : {r['score']}/100")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("SEO", r["seo"])
        col2.metric("Content", r["content"])
        col3.metric("Tech", r["tech"])
        col4.metric("UX", r["ux"])

        st.write("### ⚠️ Problèmes")
        for i in r["issues"]:
            st.warning(i)

        st.write("### 🛠 Actions correctives")
        for a in r["actions"]:
            st.success(a)

        st.write("### 📄 Extrait contenu analysé")
        st.code(r["sample"])
