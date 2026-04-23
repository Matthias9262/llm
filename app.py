import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="LLM Audit Pro", layout="wide")

st.title("🧠 LLM Readability Audit – Playwright Enhanced (SSR + SPA aware)")
st.write("Audit SEO / LLM / UX avec rendu JS réel + analyse cabinet de conseil")

urls_input = st.text_area("🔗 URLs à analyser (une par ligne)")

# ==============================
# FETCH (RENDERED HTML)
# ==============================
def fetch_html(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        return ""

# ==============================
# FRAMEWORK DETECTION
# ==============================
def detect_framework(html):
    h = html.lower()
    if "__next" in h or "next-data" in h:
        return "Next.js (SSR React)"
    if "react" in h or "data-reactroot" in h:
        return "React SPA"
    if "vue" in h:
        return "Vue.js"
    if "angular" in h:
        return "Angular"
    return "Server-rendered / Unknown"

# ==============================
# ANALYSIS
# ==============================
def analyze(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(" ")
    words = len(text.split())

    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))

    imgs = soup.find_all("img")
    missing_alt = len([i for i in imgs if not i.get("alt")])

    scripts = soup.find_all("script")

    title = soup.title.text if soup.title else None
    meta = soup.find("meta", attrs={"name": "description"})
    lang = soup.html.get("lang") if soup.html else None

    framework = detect_framework(html)

    is_spa = words < 120 and len(scripts) > 10

    # SCORES
    seo = 100
    content = 100
    tech = 100
    ux = 100

    issues = []
    actions = []

    # SEO
    if not title:
        seo -= 15
        issues.append("Title manquant")
        actions.append("Ajouter balise title optimisée")

    if h1 == 0:
        seo -= 20
        issues.append("Pas de H1")
        actions.append("Ajouter un H1 unique")

    if h2 < 2:
        seo -= 10
        issues.append("Structure H2 faible")

    if not meta:
        seo -= 10
        issues.append("Meta description absente")

    # CONTENT
    if words < 300:
        content -= 25
        issues.append("Contenu trop faible")
        actions.append("Ajouter contenu HTML indexable (FAQ, texte)")

    if is_spa:
        content -= 20
        issues.append("SPA détecté (risque SEO/LLM)")
        actions.append("Passer en SSR (Next.js / rendu serveur)")

    # TECH
    if len(scripts) > 30:
        tech -= 20
        issues.append("Trop de JS")
        actions.append("Réduire JS ou lazy load")

    # UX
    if missing_alt > 0:
        ux -= 15
        issues.append(f"{missing_alt} images sans ALT")
        actions.append("Ajouter ALT sur toutes les images")

    if not lang:
        ux -= 5
        issues.append("Lang HTML manquant")

    global_score = int((seo + content + tech + ux) / 4)

    sample = text[:500]

    return {
        "url": url,
        "framework": framework,
        "score": global_score,
        "seo": seo,
        "content": content,
        "tech": tech,
        "ux": ux,
        "words": words,
        "h1": h1,
        "h2": h2,
        "scripts": len(scripts),
        "missing_alt": missing_alt,
        "issues": issues,
        "actions": actions,
        "sample": sample
    }

# ==============================
# ROI MODEL
# ==============================
def roi(before, after):
    diff = after - before
    return {
        "traffic_gain_%": round(diff * 2.1, 2),
        "conversion_gain_%": round(diff * 0.8, 2),
        "revenue_impact_eur": round(diff * 140, 2)
    }

# ==============================
# UI
# ==============================
if urls_input:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    results = [analyze(u) for u in urls]

    df = pd.DataFrame([
        {"URL": r["url"], "Score": r["score"], "Framework": r["framework"]}
        for r in results
    ])

    st.subheader("📊 Comparaison globale")
    st.bar_chart(df.set_index("URL")["Score"])
    st.dataframe(df)

    best = max(results, key=lambda x: x["score"])
    worst = min(results, key=lambda x: x["score"])

    st.subheader("🏆 Insights")
    st.success(f"Best: {best['url']} ({best['score']})")
    st.error(f"Worst: {worst['url']} ({worst['score']})")

    st.subheader("💰 ROI estimation")
    st.write(roi(worst["score"], best["score"]))

    st.subheader("🔎 Analyse détaillée")

    for r in results:
        st.markdown(f"---\n### {r['url']}")
        st.write(f"Framework: {r['framework']}")
        st.write(f"Score global: {r['score']}/100")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("SEO", r["seo"])
        col2.metric("Content", r["content"])
        col3.metric("Tech", r["tech"])
        col4.metric("UX", r["ux"])

        st.write("### ⚠️ Issues")
        for i in r["issues"]:
            st.warning(i)

        st.write("### 🛠 Actions")
        for a in r["actions"]:
            st.success(a)

        st.write("### 📄 Content sample")
        st.code(r["sample"])
else:
    st.info("Enter URLs to start analysis")
