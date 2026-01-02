from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

KNOWN_SKILLS = {
    # IT
    "python", "javascript", "java", "django", "flask", "fastapi",
    "react", "angular", "vue", "html", "css",
    "sql", "postgresql", "mysql", "mongodb", "nosql",

    # Mechanical
    "autocad", "solidworks", "catia", "ansys",
    "manufacturing", "mechanical", "design",
    "thermal", "production",

    # Civil
    "staad", "etabs", "construction",
    "surveying", "structural", "estimation"
}

PRIMARY_SKILLS = {
    "it": {"python", "django", "javascript", "sql", "HTML", "CSS"},
    "mechanical": {"autocad", "solidworks", "ansys", "manufacturing"},
    "civil": {"staad", "etabs", "construction", "structural"}
}

def extract_clean_skills(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    words = text.split()
    return list(set(word for word in words if word in KNOWN_SKILLS))


def generate_ai_feedback(score):
    if score >= 75:
        return "Excellent match! Your resume strongly aligns with the job requirements."
    elif score >= 50:
        return "Good match. You meet many required skills, but improving a few areas will help."
    elif score >= 30:
        return "Partial match. Upskilling in key areas is recommended."
    else:
        return "Low match. Your profile does not align well with this job. Consider skill improvement."


def calculate_ai_score(resume_text, job_description, required_skills, job_category=None):
    resume_text = resume_text.lower()

    job_skills = extract_clean_skills(required_skills or "")
    resume_skills = extract_clean_skills(resume_text)

    matched_skills = []
    missing_skills = []

    PRIMARY = PRIMARY_SKILLS.get((job_category or "").lower(), set())

    total_weight = 0
    matched_weight = 0

    for skill in job_skills:
        weight = 5 if skill in PRIMARY else 1
        total_weight += weight

        if skill in resume_skills:
            matched_skills.append(skill)
            matched_weight += weight
        else:
            missing_skills.append(skill)

    # -------- BASE SKILL SCORE (60%) --------
    skill_score = (matched_weight / max(total_weight, 1)) * 60

    # -------- TEXT SIMILARITY (40%) --------
    text_score = 0
    if job_description:
        docs = [resume_text, job_description.lower()]
        tfidf = TfidfVectorizer(stop_words="english").fit_transform(docs)
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        text_score = similarity * 40

    # ✅ BASE SCORE (ONLY ONCE)
    final_score = min(skill_score + text_score, 100)

    # -------- 🔥 PRIMARY SKILL BOOST --------
    if PRIMARY:
        primary_matched = set(PRIMARY) & set(resume_skills)
        primary_ratio = len(primary_matched) / len(PRIMARY)

        if primary_ratio >= 0.5:
            final_score = max(final_score, 60)

    # -------- DOMAIN PENALTY (LAST STEP) --------
    if job_category:
        if job_category.lower() == "civil" and any(k in resume_text for k in ["python", "django", "react"]):
            final_score *= 0.6
        elif job_category.lower() == "mechanical" and any(k in resume_text for k in ["django", "react"]):
            final_score *= 0.7

    final_score = min(final_score, 100)

    feedback = generate_ai_feedback(final_score)

    return (
        round(final_score, 2),
        matched_skills,
        missing_skills,
        feedback
    )

