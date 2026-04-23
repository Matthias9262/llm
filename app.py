import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="LLM Readability Audit Pro", layout="wide")

st.title("🧠 LLM Readability Audit – Enterprise + ROI + Multi-Site + Framework Detection")
st.write("Audit avancé SEO / LLM / UX + ROI business + comparaison multi-sites + détection techno frontend")

urls_input = st.text_area("🔗 URLs à analyser (une par ligne)")

# ==============================
# FETCH
# ==============================
def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r.text
    except:
        return ""

# ==============================
# FRAMEWORK DETECTION
# ==============================
def detect_framework(html):
    html_lower = html.lower()

    if "__next" in html_lower or "next-data" in html_lower:
        return "Next.js (React SSR)"
    if "data-reactroot" in html_lower or "react" in html_lower:
        return "React SPA"
    if "vue" in html_lower or "v-bind" in html_lower:
        return "Vue.js"
    if "ng-" in html_lower or "angular" in html_lower:
        return "Angular"
    return "Unknown / Server-rendered possible"

# ==============================
# ANALYSIS CORE
# ==============================
def analyze(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(separator=" ")
    words = len(text.split())

    h1 = len(soup.find_all("h1"))
    h2 = len(soup.find_all("h2"))

    images = soup.find_all("img")
    missing_alt = len([img for img in images if not img.get("alt")])

    scripts = soup.find_all("script")
    script_count = len(scripts)

    title = soup.title.text.strip() if soup.title else None
    meta_desc = soup.find("meta", attrs={"name": "description"})

    canonical = soup.find("link", rel="canonical")
    lang = soup.html.get("lang") if soup.html else None

    is_spa = words < 80 and script_count > 10

    framework = detect_framework(html)

    # SCORES
    seo = 100
    content = 100
    tech = 100
    ux = 100

    issues = []

    if not title:
        seo -= 15
        issues.append("Missing title")

    if h1 == 0:
        seo -= 20
        issues.append("No H1")

    if h2 < 2:
        seo -= 10
        issues.append("Weak H2 structure")

    if not meta_desc:
        seo -= 10
        issues.append("Missing meta description")

    if words < 300:
        content -= 25
        issues.append("Low content density")

    if is_spa:
        content -= 20
        issues.append("SPA-like JS rendered content")

    if script_count > 30:
        tech -= 25
        issues.append("Heavy JavaScript usage")

    if missing_alt > 0:
        ux -= 20
        issues.append("Missing image ALT attributes")

    if not lang:
        ux -= 5
        issues.append("Missing lang attribute")

    global_score = int((seo + content + tech + ux) / 4)

    return {
        "url": url,
        "seo": seo,
        "content": content,
        "tech": tech,
        "ux": ux,
        "global": global_score,
        "words": words,
        "h1": h1,
        "h2": h2,
        "scripts": script_count,
        "missing_alt": missing_alt,
        "framework": framework,
        "issues": issues
    }

# ==============================
# ROI MODEL
# ==============================
def estimate_roi(score_before, score_after):
    improvement = score_after - score_before
    traffic_gain = improvement * 1.8  # heuristic
    conversion_gain = improvement * 0.6
    revenue_impact = improvement * 120  # arbitrary business multiplier

    return {
        "traffic_gain_%": round(traffic_gain, 2),
        "conversion_gain_%": round(conversion_gain, 2),
        "estimated_revenue_impact_eur": round(revenue_impact, 2)
    }

# ==============================
# UI
# ==============================
if urls_input:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    results = []

    for u in urls:
        results.append(analyze(u))

    st.subheader("📊 Multi-site comparison")

    df = pd.DataFrame([
        {"URL": r["url"], "Score": r["global"], "Framework": r["framework"]}
        for r in results
    ])

    st.bar_chart(df.set_index("URL")["Score"])

    st.dataframe(df)

    # BEST / WORST
    best = max(results, key=lambda x: x["global"])
    worst = min(results, key=lambda x: x["global"])

    st.subheader("🏆 Insights")
    st.success(f"Best site: {best['url']} ({best['global']}/100)")
    st.error(f"Worst site: {worst['url']} ({worst['global']}/100)")

    # ROI SIMULATION
    st.subheader("💰 ROI estimation (optimization impact)")

    roi = estimate_roi(worst["global"], best["global"])

    st.write(roi)

    # FRAMEWORK BREAKDOWN
    st.subheader("⚙️ Framework detection")
    st.write(df[["URL", "Framework"]])

    # ISSUES DETAIL
    st.subheader("⚠️ Detailed issues per site")
    for r in results:
        st.write("---")
        st.write(r["url"])
        st.write(r["issues"])
else:
    st.info("Enter multiple URLs (one per line) to start analysis")
