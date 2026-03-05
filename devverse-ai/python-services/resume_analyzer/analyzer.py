"""
Enterprise-Grade ATS Resume Analyzer
Replicates scoring logic from Workday, Greenhouse, Lever, and Taleo.
Analyzes 15+ dimensions of resume quality.
"""

import os
import re
import math
from collections import Counter
from PyPDF2 import PdfReader

# ============================================================
# SKILLS BANK — Industry Standard Taxonomy
# ============================================================
SKILLS_BANK = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "kotlin", "swift", "php", "scala", "r", "matlab", "perl",
        "haskell", "lua", "dart", "elixir", "julia", "cobol", "fortran", "assembly"
    ],
    "Frontend": [
        "react", "vue", "angular", "html", "css", "html5", "css3", "sass", "less",
        "tailwindcss", "bootstrap", "material ui", "next.js", "nuxt", "svelte",
        "redux", "graphql", "webpack", "vite", "babel", "jquery", "gatsby",
        "styled components", "emotion", "storybook", "cypress", "jest", "playwright"
    ],
    "Backend": [
        "node.js", "express", "flask", "django", "fastapi", "spring", "spring boot",
        "rails", "laravel", "asp.net", ".net", "nestjs", "fastify", "hapi",
        "grpc", "rest api", "restful", "soap", "graphql", "websockets", "microservices",
        "kafka", "rabbitmq", "celery", "redis", "nginx", "apache", "tomcat"
    ],
    "Mobile": [
        "android", "ios", "react native", "flutter", "xamarin", "ionic",
        "swift", "kotlin", "objective-c", "expo", "capacitor"
    ],
    "Databases": [
        "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "dynamodb",
        "elasticsearch", "cassandra", "mariadb", "neo4j", "firebase", "supabase",
        "cockroachdb", "influxdb", "clickhouse", "snowflake", "bigquery", "redshift",
        "sql", "nosql", "database design", "query optimization", "indexing"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
        "jenkins", "github actions", "gitlab ci", "circleci", "travis ci", "ci/cd",
        "linux", "ansible", "puppet", "chef", "helm", "istio", "prometheus", "grafana",
        "elk stack", "datadog", "new relic", "cloudformation", "pulumi", "vagrant",
        "serverless", "lambda", "ec2", "s3", "rds", "vpc", "iam", "cloudwatch"
    ],
    "AI & Data Science": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "nlp", "computer vision", "natural language processing",
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy",
        "data analysis", "data visualization", "statistics", "apache spark",
        "hadoop", "data pipeline", "etl", "feature engineering", "model deployment",
        "mlops", "llm", "langchain", "openai", "hugging face", "transformers",
        "reinforcement learning", "generative ai", "rag"
    ],
    "Security": [
        "cybersecurity", "penetration testing", "ethical hacking", "vulnerability assessment",
        "owasp", "ssl", "tls", "encryption", "oauth", "jwt", "sso", "firewalls",
        "siem", "soc", "incident response", "network security"
    ],
    "Architecture & Design": [
        "system design", "microservices", "event driven", "domain driven design",
        "solid principles", "design patterns", "api design", "distributed systems",
        "high availability", "fault tolerance", "scalability", "load balancing",
        "caching", "message queue", "service mesh"
    ],
    "Tools & Collaboration": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "figma",
        "postman", "swagger", "openapi", "vscode", "intellij", "eclipse",
        "tableau", "power bi", "looker", "notion", "slack", "agile",
        "scrum", "kanban", "code review"
    ],
    "Testing": [
        "unit testing", "integration testing", "e2e testing", "test driven development",
        "tdd", "bdd", "selenium", "playwright", "cypress", "jest", "pytest",
        "junit", "mocha", "chai", "testing library", "performance testing"
    ],
}

# Flatten all skills for lookup
ALL_SKILLS_FLAT = set()
for skills in SKILLS_BANK.values():
    ALL_SKILLS_FLAT.update(skills)

# ============================================================
# ATS CHECKS CONFIG
# ============================================================
SECTION_KEYWORDS = {
    "contact":      ["email", "phone", "linkedin", "github", "portfolio", "address", "@"],
    "summary":      ["summary", "objective", "profile", "about me", "professional summary", "career objective", "overview"],
    "education":    ["education", "academic", "degree", "university", "college", "b.tech", "b.e", "m.tech", "bachelor", "master", "phd", "bsc", "msc", "b.s.", "m.s.", "diploma", "graduation"],
    "experience":   ["experience", "work experience", "employment", "internship", "intern", "professional experience", "career", "work history"],
    "projects":     ["projects", "project", "personal projects", "academic projects", "open source", "portfolio projects"],
    "skills":       ["skills", "technical skills", "core competencies", "technologies", "tech stack", "expertise", "competencies", "tools"],
    "achievements": ["achievement", "award", "certification", "honors", "recognition", "accomplishment", "prize", "scholarship"],
    "certifications": ["certification", "certified", "certificate", "aws certified", "google certified", "microsoft certified"],
    "publications": ["publication", "paper", "research", "journal", "conference", "patent"],
    "leadership":   ["leadership", "team lead", "management", "mentoring", "volunteering", "community"],
}

ACTION_VERBS = {
    "high_impact": [
        "architected", "spearheaded", "revolutionized", "pioneered", "transformed",
        "orchestrated", "championed", "catapulted", "accelerated", "scaled",
        "established", "launched", "founded"
    ],
    "achievement": [
        "achieved", "delivered", "exceeded", "surpassed", "accomplished",
        "attained", "completed", "finished", "produced", "generated"
    ],
    "technical": [
        "developed", "built", "designed", "implemented", "engineered", "programmed",
        "deployed", "automated", "optimized", "refactored", "migrated", "integrated",
        "configured", "maintained", "debugged", "tested", "documented"
    ],
    "leadership": [
        "led", "managed", "mentored", "coached", "directed", "supervised",
        "coordinated", "collaborated", "partnered", "facilitated"
    ],
    "improvement": [
        "improved", "enhanced", "upgraded", "streamlined", "reduced", "increased",
        "boosted", "cut", "eliminated", "resolved", "fixed"
    ],
}

ALL_ACTION_VERBS = []
for group in ACTION_VERBS.values():
    ALL_ACTION_VERBS.extend(group)

EDUCATION_LEVELS = {
    "phd":      ["ph.d", "phd", "doctorate"],
    "master":   ["master", "m.tech", "m.s.", "msc", "m.e.", "mba", "m.b.a."],
    "bachelor": ["bachelor", "b.tech", "b.e.", "bsc", "b.s.", "b.a.", "undergraduate"],
    "associate":["associate", "diploma"],
    "high_school": ["high school", "12th", "10+2", "secondary"],
}

GUNK_PATTERNS = [
    (r'\|', "Pipe characters may confuse ATS parsers"),
    (r'[│┃▌▐]', "Special unicode characters may not parse correctly"),
    (r'(?i)objective:', "Outdated 'Objective:' section — use 'Professional Summary' instead"),
]

DESIRED_WORD_RANGE = (450, 900)

# ============================================================
# EXTRACT TEXT
# ============================================================
def extract_text(filepath):
    try:
        reader = PdfReader(filepath)
        raw_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                raw_text += t + "\n"
        return raw_text
    except Exception as e:
        return ""


# ============================================================
# CHECK 1: CONTACT INFO
# ============================================================
def check_contact_info(text, text_lower):
    results = {"score": 0, "max": 10, "found": [], "missing": []}
    
    if re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', text):
        results["score"] += 3; results["found"].append("Email")
    else:
        results["missing"].append("Email address")

    if re.search(r'(\+?\d[\d\s\-().]{7,})', text):
        results["score"] += 2; results["found"].append("Phone")
    else:
        results["missing"].append("Phone number")

    if "linkedin" in text_lower:
        results["score"] += 2; results["found"].append("LinkedIn")
    else:
        results["missing"].append("LinkedIn URL")

    if "github" in text_lower:
        results["score"] += 2; results["found"].append("GitHub")
    else:
        results["missing"].append("GitHub URL")

    if re.search(r'https?://', text):
        results["score"] += 1; results["found"].append("Portfolio/Website")

    results["score"] = min(results["score"], 10)
    results["detail"] = f"Found: {', '.join(results['found']) or 'None'}"
    return results


# ============================================================
# CHECK 2: SECTIONS COMPLETENESS
# ============================================================
def check_sections(text, text_lower):
    found = {}
    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found[section] = True
                break

    critical  = ["summary", "education", "experience", "skills"]
    important = ["projects", "achievements", "certifications"]
    
    crit_count = sum(1 for s in critical if s in found)
    imp_count  = sum(1 for s in important if s in found)
    
    score = crit_count * 4 + imp_count * 2
    score = min(score, 20)

    return {
        "score": score, "max": 20,
        "found": list(found.keys()),
        "missing": [s for s in critical if s not in found],
        "detail": f"{len(found)}/{len(SECTION_KEYWORDS)} sections detected"
    }


# ============================================================
# CHECK 3: SKILLS MATCH
# ============================================================
def check_skills(text_lower):
    skills_by_cat = {}
    total = 0
    for cat, skills in SKILLS_BANK.items():
        matched = []
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(skill)
        if matched:
            skills_by_cat[cat] = matched
            total += len(matched)

    score = min(total * 2, 25)
    return {
        "score": score, "max": 25,
        "by_category": skills_by_cat,
        "flat": [s for cat in skills_by_cat.values() for s in cat],
        "total": total,
        "detail": f"{total} skills across {len(skills_by_cat)} categories"
    }


# ============================================================
# CHECK 4: QUANTIFIED ACHIEVEMENTS
# ============================================================
def check_quantification(text):
    patterns = [
        r'\d+%',                           # percentages
        r'\$\s*\d+(?:[kKmMbB])?',         # money amounts
        r'\d+\s*(?:x|times|fold)',         # multipliers
        r'\d+\+?\s*(?:users|customers|clients|engineers|members|employees)',
        r'(?:saved|reduced|improved|increased|generated)\s+[\w\s]*\d+',
        r'\d+\s*(?:ms|seconds|minutes|hours|days|weeks)\s+(?:faster|reduction|improvement)',
    ]
    matches = []
    for p in patterns:
        found = re.findall(p, text, re.IGNORECASE)
        matches.extend(found)
    
    score = min(len(matches) * 4, 15)
    return {
        "score": score, "max": 15,
        "count": len(matches),
        "examples": list(set(matches))[:5],
        "detail": f"{len(matches)} quantified achievement(s) found"
    }


# ============================================================
# CHECK 5: ACTION VERBS
# ============================================================
def check_action_verbs(text_lower):
    found_high = [v for v in ACTION_VERBS["high_impact"] if f' {v}' in text_lower or text_lower.startswith(v)]
    found_all  = [v for v in ALL_ACTION_VERBS if f' {v}' in text_lower or text_lower.startswith(v)]
    
    score = min(len(found_high) * 2 + len(found_all), 10)
    return {
        "score": score, "max": 10,
        "found": list(set(found_all)),
        "high_impact": list(set(found_high)),
        "detail": f"{len(set(found_all))} action verbs ({len(set(found_high))} high-impact)"
    }


# ============================================================
# CHECK 6: EDUCATION LEVEL
# ============================================================
def check_education(text_lower):
    level = "none"
    for lvl, keywords in EDUCATION_LEVELS.items():
        for kw in keywords:
            if kw in text_lower:
                level = lvl
                break
        if level != "none":
            break

    level_scores = {"phd": 8, "master": 8, "bachelor": 8, "associate": 5, "high_school": 3, "none": 0}
    score = level_scores.get(level, 0)

    # Check for GPA / CGPA
    has_gpa = bool(re.search(r'(?:gpa|cgpa|grade)\s*[:\-]?\s*\d+\.?\d*', text_lower))
    if has_gpa:
        score = min(score + 2, 10)

    return {
        "score": score, "max": 10,
        "level": level,
        "has_gpa": has_gpa,
        "detail": f"Detected: {level.replace('_', ' ').title()}{' | CGPA listed' if has_gpa else ''}"
    }


# ============================================================
# CHECK 7: CONTENT LENGTH & DEPTH
# ============================================================
def check_length(text):
    words = len(text.split())
    sentences = max(len(re.findall(r'[.!?]+', text)), 1)
    avg_sentence_len = words / sentences

    if DESIRED_WORD_RANGE[0] <= words <= DESIRED_WORD_RANGE[1]:
        score = 10
        note = "Ideal length"
    elif words < 300:
        score = 3
        note = "Too short — add more detail"
    elif words < 450:
        score = 6
        note = "Slightly short"
    elif words <= 1200:
        score = 8
        note = "Slightly long for 1 page"
    else:
        score = 5
        note = "Very long — consider trimming"

    return {
        "score": score, "max": 10,
        "word_count": words,
        "sentences": sentences,
        "detail": f"{words} words — {note}"
    }


# ============================================================
# CHECK 8: ATS FORMATTING SIGNALS
# ============================================================
def check_formatting(text):
    issues = []
    bonuses = []

    # Check for ATS-unfriendly patterns
    for pattern, msg in GUNK_PATTERNS:
        if re.search(pattern, text):
            issues.append(msg)

    # Check for proper date formatting
    date_patterns = [
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b',
        r'\b\d{1,2}/\d{4}\b',
        r'\b20\d{2}\s*[-–]\s*(?:20\d{2}|present|current)\b',
    ]
    has_dates = any(re.search(p, text, re.IGNORECASE) for p in date_patterns)
    if has_dates:
        bonuses.append("Proper date formatting")
    else:
        issues.append("Add clear date ranges (e.g., Jan 2022 – Dec 2023)")

    # Check for standard headers (ATS looks for these)
    has_bullets = bool(re.search(r'[•\-\*→]', text))
    if has_bullets:
        bonuses.append("Bullet points used")
    else:
        issues.append("Use bullet points for experience/skills sections")

    score = max(0, 10 - len(issues) * 2) + min(len(bonuses), 3)
    score = min(score, 10)

    return {
        "score": score, "max": 10,
        "issues": issues,
        "bonuses": bonuses,
        "detail": f"{len(bonuses)} good signals, {len(issues)} potential issues"
    }


# ============================================================
# CHECK 9: EXPERIENCE DETECTION
# ============================================================
def check_experience(text, text_lower):
    # Extract years of experience from text
    exp_patterns = [
        r'(\d+)\+?\s+years?\s+(?:of\s+)?(?:experience|exp)',
        r'(\d+)\s+years?\s+(?:in|of)',
        r'experience\s+of\s+(\d+)\+?\s+years?',
    ]
    years = 0
    for p in exp_patterns:
        m = re.search(p, text_lower)
        if m:
            years = max(years, int(m.group(1)))

    # Count job titles
    title_patterns = r'(?i)\b(software engineer|developer|architect|analyst|manager|lead|intern|senior|junior|full.?stack|backend|frontend|devops|data\s+scientist)\b'
    titles = list(set(re.findall(title_patterns, text, re.IGNORECASE)))

    # Score based on years and clarity
    if years >= 5:
        score = 10
    elif years >= 3:
        score = 8
    elif years >= 1:
        score = 6
    elif len(titles) > 0:
        score = 5
    else:
        score = 2

    return {
        "score": score, "max": 10,
        "years": years,
        "titles_detected": [t.title() for t in titles[:5]],
        "detail": f"{years}+ years detected, roles: {', '.join(titles[:3]) or 'Not explicitly stated'}"
    }


# ============================================================
# CHECK 10: KEYWORD DENSITY (JOB MATCH)
# ============================================================
def check_job_match(text_lower, job_description):
    if not job_description or len(job_description.strip()) < 20:
        return {
            "score": 0, "max": 0,  # Not scored if no JD
            "match_pct": 0,
            "matched": [],
            "missing": [],
            "detail": "No job description provided"
        }

    jd_lower = job_description.lower()
    
    # Extract JD skills
    jd_skills = []
    for skills in SKILLS_BANK.values():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, jd_lower):
                jd_skills.append(skill)

    if not jd_skills:
        return {"score": 0, "max": 0, "match_pct": 0, "matched": [], "missing": [], "detail": "No known skills in JD"}

    matched = [s for s in jd_skills if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]
    missing = [s for s in jd_skills if s not in matched]
    match_pct = min(int((len(matched) / len(jd_skills)) * 100), 100)

    # Keyword density check — how often JD keywords appear in resume
    word_count = max(len(text_lower.split()), 1)
    density_bonus = min(sum(text_lower.count(s) for s in matched) / word_count * 100, 5)
    score = min(int(match_pct * 0.2 + density_bonus), 20)

    return {
        "score": score, "max": 20,
        "match_pct": match_pct,
        "matched": matched,
        "missing": missing[:10],
        "total_jd_skills": len(jd_skills),
        "detail": f"{match_pct}% skill match ({len(matched)}/{len(jd_skills)} JD skills)"
    }


# ============================================================
# GENERATE SMART SUGGESTIONS
# ============================================================
def generate_suggestions(checks, text, score):
    suggestions = []

    c = checks
    
    if not c["contact"]["found"] or len(c["contact"]["missing"]) > 0:
        for m in c["contact"]["missing"]:
            suggestions.append({"type": "error", "text": f"Missing {m} — top ATS systems rank this as critical"})

    if c["sections"]["score"] < 16:
        for m in c["sections"]["missing"]:
            suggestions.append({"type": "warning", "text": f"Add a '{m.title()}' section — it\'s expected by ATS parsers"})

    if c["quantification"]["count"] < 3:
        suggestions.append({"type": "warning", "text": "Quantify your achievements: use numbers like '40% faster', '$2M revenue', '50,000 users'"})

    if c["action_verbs"]["score"] < 6:
        suggestions.append({"type": "info", "text": "Use high-impact verbs: Architected, Spearheaded, Scaled, Orchestrated, Delivered"})

    if c["skills"]["total"] < 10:
        suggestions.append({"type": "warning", "text": f"Only {c['skills']['total']} skills detected — ATS ranks higher with 10–20 relevant skills"})

    if c["formatting"]["issues"]:
        for issue in c["formatting"]["issues"][:2]:
            suggestions.append({"type": "error", "text": f"Formatting: {issue}"})

    if c["length"]["word_count"] < 400:
        suggestions.append({"type": "warning", "text": "Resume is too short. Ideal length is 450–900 words. Expand projects/experience."})
    elif c["length"]["word_count"] > 1000:
        suggestions.append({"type": "info", "text": "Resume may be too long. Trim to 1–2 pages (450–900 words) for better ATS parsing."})

    if c["education"]["level"] == "none":
        suggestions.append({"type": "error", "text": "Education section not detected — ensure it has clear degree names"})

    if not re.search(r'\d+', text):
        suggestions.append({"type": "warning", "text": "No numbers found — numbers signal impact and get picked up by ATS keyword scanners"})

    if score >= 80:
        suggestions.append({"type": "success", "text": "Excellent ATS score! Your resume should pass most automated screening systems."})
    elif score >= 60:
        suggestions.append({"type": "success", "text": "Good score. Address the warnings above to reach 80+ and pass top company filters."})
    else:
        suggestions.append({"type": "error", "text": "Score below 60. Most ATS will reject this before human review. Fix red issues first."})

    return suggestions[:8]


# ============================================================
# MAIN ANALYZE FUNCTION
# ============================================================
def analyze_resume(filepath, job_description=""):
    text = extract_text(filepath)
    if not text or len(text.strip()) < 50:
        return {"error": "Could not extract text from PDF. Ensure it is a text-based PDF (not a scanned image)."}

    text_lower = text.lower()

    checks = {
        "contact":        check_contact_info(text, text_lower),
        "sections":       check_sections(text, text_lower),
        "skills":         check_skills(text_lower),
        "quantification": check_quantification(text),
        "action_verbs":   check_action_verbs(text_lower),
        "education":      check_education(text_lower),
        "length":         check_length(text),
        "formatting":     check_formatting(text),
        "experience":     check_experience(text, text_lower),
    }

    # Job match (optional bonus)
    job_match = check_job_match(text_lower, job_description)
    if job_match["max"] > 0:
        checks["job_match"] = job_match

    # Compute ATS score
    weighted_total = sum(v["score"] for v in checks.values())
    weighted_max   = sum(v["max"] for v in checks.values())
    ats_score = min(int((weighted_total / max(weighted_max, 1)) * 100), 100)

    suggestions = generate_suggestions(checks, text, ats_score)

    # Determine ATS tier (like real recruiters use)
    if ats_score >= 85:
        tier = {"label": "Top Tier", "color": "green", "desc": "Strong match — will pass most enterprise ATS"}
    elif ats_score >= 70:
        tier = {"label": "Above Average", "color": "blue", "desc": "Likely to pass mid-tier company ATS filters"}
    elif ats_score >= 55:
        tier = {"label": "Average", "color": "yellow", "desc": "Will pass some ATS — needs improvement for top companies"}
    else:
        tier = {"label": "Below Average", "color": "red", "desc": "Likely to be filtered out by automated screening"}

    return {
        "ats_score":          ats_score,
        "tier":               tier,
        "checks":             checks,
        "score_breakdown":    {k: {"score": v["score"], "max": v["max"], "detail": v.get("detail", "")} for k, v in checks.items()},
        "sections_found":     checks["sections"]["found"],
        "skills_by_category": checks["skills"]["by_category"],
        "skills_flat":        checks["skills"]["flat"],
        "action_verbs":       checks["action_verbs"]["found"],
        "high_impact_verbs":  checks["action_verbs"]["high_impact"],
        "experience_years":   checks["experience"]["years"],
        "job_titles":         checks["experience"]["titles_detected"],
        "word_count":         checks["length"]["word_count"],
        "quantified_count":   checks["quantification"]["count"],
        "quantified_examples":checks["quantification"]["examples"],
        "formatting_issues":  checks["formatting"]["issues"],
        "formatting_bonuses": checks["formatting"]["bonuses"],
        "education_level":    checks["education"]["level"],
        "contact_found":      checks["contact"]["found"],
        "contact_missing":    checks["contact"]["missing"],
        "job_match_score":    job_match.get("match_pct", 0),
        "matched_skills":     job_match.get("matched", []),
        "missing_jd_skills":  job_match.get("missing", []),
        "suggestions":        suggestions,
    }
