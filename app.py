import os
import re

from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from google import genai
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.6-flash"

client = None


if GEMINI_API_KEY:

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print("Gemini client initialized.")

    except Exception as e:

        print("Gemini initialization failed:")
        print(e)

        client = None

else:

    print("Gemini API key not found.")
    print("Local fallback analysis will be used.")


# =========================================================
# SKILLS DATABASE
# =========================================================

SKILLS = [

    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "php",
    "ruby",
    "go",

    # Web
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "node",
    "express",
    "bootstrap",
    "tailwind",

    # Backend
    "flask",
    "django",
    "spring",
    "spring boot",
    "rest api",
    "api",

    # Database
    "mysql",
    "mongodb",
    "postgresql",
    "sql",
    "sqlite",
    "oracle",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "data analysis",
    "data analytics",
    "pandas",
    "numpy",
    "matplotlib",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "nlp",
    "llm",
    "generative ai",

    # Cloud
    "aws",
    "azure",
    "google cloud",
    "docker",
    "kubernetes",

    # Tools
    "git",
    "github",
    "gitlab",
    "power bi",
    "excel",
    "tableau",
    "jira",
    "figma",
    "postman",

    # Automation
    "n8n",
    "zapier",
    "make",
    "automation",

    # Soft Skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "time management",
    "adaptability"
]


SOFT_SKILLS = [

    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "time management",
    "adaptability"

]


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(pdf_path):

    text = ""

    try:

        reader = PdfReader(pdf_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        return text.strip()

    except Exception as e:

        print("PDF Extraction Error:")
        print(e)

        return ""


# =========================================================
# FIND SKILLS
# =========================================================

def find_skills(text):

    text_lower = text.lower()

    found = []

    for skill in SKILLS:

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill.lower())
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text_lower):

            found.append(skill)

    return found


# =========================================================
# FORMAT LIST
# =========================================================

def format_list(items):

    if not items:

        return "- Not mentioned"

    return "\n".join(
        "- " + str(item).title()
        for item in items
    )


# =========================================================
# ATS SCORE
# =========================================================

def calculate_ats_score(resume_text):

    score = 0

    text = resume_text.lower()

    word_count = len(resume_text.split())


    # Content length
    if word_count >= 250:

        score += 20

    elif word_count >= 150:

        score += 15

    elif word_count >= 80:

        score += 10

    else:

        score += 5


    # Sections
    sections = [

        "education",
        "experience",
        "skills",
        "project",
        "summary",
        "objective"

    ]

    section_count = 0

    for section in sections:

        if section in text:

            section_count += 1


    score += min(section_count * 5, 30)


    # Skills
    skills = find_skills(resume_text)

    if len(skills) >= 10:

        score += 25

    elif len(skills) >= 6:

        score += 20

    elif len(skills) >= 3:

        score += 15

    else:

        score += 5


    # Email
    if re.search(
        r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        resume_text
    ):

        score += 10


    # Phone
    if re.search(
        r"\b\d{10}\b",
        resume_text
    ):

        score += 5


    return min(score, 100)


# =========================================================
# JOB ROLE SUGGESTIONS
# =========================================================

def suggest_job_roles(skills):

    roles = []

    if "python" in skills:

        roles.append(
            "Python Developer"
        )

    if "java" in skills:

        roles.append(
            "Java Developer"
        )

    if (
        "javascript" in skills
        or "react" in skills
    ):

        roles.append(
            "Web Developer"
        )

    if (
        "machine learning" in skills
        or "scikit-learn" in skills
    ):

        roles.append(
            "Machine Learning Intern"
        )

    if (
        "artificial intelligence" in skills
        or "ai" in skills
    ):

        roles.append(
            "AI/ML Intern"
        )

    if (
        "data analysis" in skills
        or "power bi" in skills
        or "excel" in skills
    ):

        roles.append(
            "Data Analyst"
        )

    if (
        "mongodb" in skills
        or "sql" in skills
        or "mysql" in skills
    ):

        roles.append(
            "Backend / Database Developer"
        )

    if (
        "n8n" in skills
        or "automation" in skills
    ):

        roles.append(
            "AI Automation / Automation Intern"
        )


    if not roles:

        roles.append(
            "Software Developer Intern"
        )


    return roles


# =========================================================
# FALLBACK RESUME ANALYSIS
# =========================================================

def fallback_resume_analysis(resume_text):

    skills = find_skills(resume_text)

    score = calculate_ats_score(
        resume_text
    )

    text_lower = resume_text.lower()


    # -------------------------
    # Strengths
    # -------------------------

    strengths = []


    if len(skills) >= 5:

        strengths.append(
            "Resume contains multiple relevant technical skills."
        )


    if "project" in text_lower:

        strengths.append(
            "Projects section is present."
        )


    if "education" in text_lower:

        strengths.append(
            "Education information is present."
        )


    if (
        "experience" in text_lower
        or "internship" in text_lower
    ):

        strengths.append(
            "Experience or internship information is present."
        )


    if not strengths:

        strengths.append(
            "Resume text was successfully extracted."
        )


    # -------------------------
    # Weaknesses
    # -------------------------

    weaknesses = []


    if len(resume_text.split()) < 150:

        weaknesses.append(
            "Resume appears to contain limited content."
        )


    if (
        "summary" not in text_lower
        and "objective" not in text_lower
    ):

        weaknesses.append(
            "Consider adding a professional summary."
        )


    if "project" not in text_lower:

        weaknesses.append(
            "Consider adding relevant projects."
        )


    if (
        "experience" not in text_lower
        and "internship" not in text_lower
    ):

        weaknesses.append(
            "Consider adding internship or practical experience."
        )


    if not weaknesses:

        weaknesses.append(
            "Review formatting and keep information concise."
        )


    # -------------------------
    # Missing Improvements
    # -------------------------

    missing = [

        "ATS-friendly formatting",
        "Quantifiable achievements",
        "Relevant job-specific keywords"

    ]


    # -------------------------
    # Technical skills
    # -------------------------

    technical_skills = [

        skill
        for skill in skills
        if skill not in SOFT_SKILLS

    ]


    # -------------------------
    # Soft skills
    # -------------------------

    soft_skills = [

        skill
        for skill in skills
        if skill in SOFT_SKILLS

    ]


    # -------------------------
    # Education
    # -------------------------

    education = (

        "Education information found in resume."

        if "education" in text_lower

        else

        "Not clearly mentioned."

    )


    # -------------------------
    # Projects
    # -------------------------

    projects = (

        "Project information found in resume."

        if "project" in text_lower

        else

        "Not clearly mentioned."

    )


    # -------------------------
    # Experience
    # -------------------------

    experience = (

        "Experience or internship information found in resume."

        if (
            "experience" in text_lower
            or "internship" in text_lower
        )

        else

        "Not clearly mentioned."

    )


    # -------------------------
    # Roles
    # -------------------------

    roles = suggest_job_roles(
        skills
    )


    return f"""

## RESUME SCORE
{score}/100

## CANDIDATE SUMMARY
The resume has been successfully processed.
The analysis below is based on the text extracted
from the uploaded resume.

## KEY SKILLS
{format_list(skills)}

## TECHNICAL SKILLS
{format_list(technical_skills)}

## SOFT SKILLS
{format_list(soft_skills)}

## EDUCATION
{education}

## PROJECTS
{projects}

## EXPERIENCE
{experience}

## STRENGTHS
{format_list(strengths)}

## WEAKNESSES
{format_list(weaknesses)}

## MISSING SKILLS
{format_list(missing)}

## ATS SUGGESTIONS
- Use standard section headings.
- Add job-specific keywords.
- Add measurable achievements where possible.
- Keep formatting simple and ATS-friendly.
- Use clear descriptions for projects and experience.

## SUITABLE JOB ROLES
{format_list(roles)}

## ANALYSIS MODE
Local fallback analysis was used because Gemini AI
was temporarily unavailable.

"""


# =========================================================
# FALLBACK JOB MATCH
# =========================================================

def fallback_job_match(
    resume_text,
    job_description
):

    resume_skills = set(
        find_skills(resume_text)
    )

    job_skills = set(
        find_skills(job_description)
    )


    matching = sorted(
        resume_skills.intersection(
            job_skills
        )
    )


    missing = sorted(
        job_skills.difference(
            resume_skills
        )
    )


    if len(job_skills) > 0:

        percentage = int(
            (
                len(matching)
                /
                len(job_skills)
            )
            * 100
        )

    else:

        percentage = 0


    # Qualifications

    qualifications = []

    resume_lower = resume_text.lower()

    jd_lower = job_description.lower()


    education_words = [

        "b.tech",
        "btech",
        "b.e",
        "bachelor",
        "degree",
        "engineering",
        "computer science",
        "information technology"

    ]


    for word in education_words:

        if (
            word in resume_lower
            and word in jd_lower
        ):

            qualifications.append(
                word
            )


    if not qualifications:

        qualifications.append(
            "Compare education requirements manually."
        )


    # Suggestions

    suggestions = []


    if missing:

        suggestions.append(
            "Add relevant skills from the job description only if you genuinely possess them."
        )


    suggestions.append(
        "Use important job-specific keywords naturally in your resume."
    )

    suggestions.append(
        "Add measurable achievements to projects and experience."
    )


    return f"""

## JOB MATCH PERCENTAGE
{percentage}%

## MATCHING SKILLS
{format_list(matching)}

## JOB MISSING SKILLS
{format_list(missing)}

## MATCHING QUALIFICATIONS
{format_list(qualifications)}

## EXPERIENCE MATCH
Review your experience descriptions against the
responsibilities listed in the job description.

## TECHNICAL MATCH
Matching technical skills:
{format_list(matching)}

## MISSING ATS KEYWORDS
{format_list(missing)}

## JOB-SPECIFIC SUGGESTIONS
{format_list(suggestions)}

## FINAL SUMMARY
The calculated job match is based on detected
skills appearing in both the resume and job description.

## ANALYSIS MODE
Local fallback job matching was used because
Gemini AI was temporarily unavailable.

"""


# =========================================================
# GEMINI AI ANALYSIS
# =========================================================

def gemini_analysis(
    resume_text,
    job_description
):

    prompt = f"""

You are an expert Resume Analyzer and ATS Job Matching System.

Analyze the resume and job description.

RESUME:

{resume_text}


JOB DESCRIPTION:

{job_description}


Return the analysis using exactly these headings:

## RESUME SCORE

## CANDIDATE SUMMARY

## KEY SKILLS

## TECHNICAL SKILLS

## SOFT SKILLS

## EDUCATION

## PROJECTS

## EXPERIENCE

## STRENGTHS

## WEAKNESSES

## MISSING SKILLS

## ATS SUGGESTIONS

## SUITABLE JOB ROLES

## JOB MATCH PERCENTAGE

## MATCHING SKILLS

## JOB MISSING SKILLS

## MATCHING QUALIFICATIONS

## EXPERIENCE MATCH

## TECHNICAL MATCH

## MISSING ATS KEYWORDS

## JOB-SPECIFIC SUGGESTIONS

## FINAL SUMMARY

Rules:

- Do not invent information.
- Do not create fake skills.
- Do not create fake experience.
- Base everything on the supplied resume and job description.
- Resume Score must be from 0 to 100.
- Job Match Percentage must be from 0 to 100.
- Use bullet points where appropriate.

"""


    try:

        print("Trying Gemini AI...")


        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt

        )


        if response and response.text:

            print(
                "Gemini AI successful."
            )

            return response.text.strip()


        print(
            "Gemini returned empty response."
        )

        return None


    except Exception as e:

        print(
            "Gemini unavailable."
        )

        print(
            "Reason:",
            e
        )

        return None


# =========================================================
# PARSE ANALYSIS RESULT
# =========================================================

def parse_analysis_result(result):

    if not result:

        return {

            "resume_score": 0,

            "job_match": 0,

            "sections": {}

        }


    # Remove accidental escaped markdown
    result = result.replace(
        "\\##",
        "##"
    )


    sections = {}

    current_section = None

    current_content = []


    for line in result.splitlines():

        line = line.strip()


        # Heading
        if line.startswith("##"):

            if current_section:

                sections[
                    current_section
                ] = current_content


            current_section = (
                line
                .replace(
                    "##",
                    "",
                    1
                )
                .strip()
            )


            current_content = []


        elif line:

            current_content.append(
                line
            )


    # Save final section

    if current_section:

        sections[
            current_section
        ] = current_content


    # =====================================================
    # RESUME SCORE
    # =====================================================

    resume_score = 0

    score_text = sections.get(
        "RESUME SCORE",
        []
    )


    for line in score_text:

        match = re.search(
            r"(\d{1,3})\s*/\s*100",
            line
        )


        if match:

            resume_score = int(
                match.group(1)
            )

            break


    # =====================================================
    # JOB MATCH
    # =====================================================

    job_match = 0

    job_match_text = sections.get(
        "JOB MATCH PERCENTAGE",
        []
    )


    for line in job_match_text:

        match = re.search(
            r"(\d{1,3})\s*%",
            line
        )


        if match:

            job_match = int(
                match.group(1)
            )

            break


    # =====================================================
    # NORMALIZE SCORES
    # =====================================================

    resume_score = max(
        0,
        min(
            resume_score,
            100
        )
    )


    job_match = max(
        0,
        min(
            job_match,
            100
        )
    )


    return {

        "resume_score":
            resume_score,

        "job_match":
            job_match,

        "sections":
            sections

    }


# =========================================================
# HOME ROUTE
# =========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    resume_text = ""

    job_description = ""

    analysis_result = None

    analysis_data = None

    error = None


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":


        resume_file = request.files.get(
            "resume"
        )


        job_description = request.form.get(
            "job_description",
            ""
        ).strip()


        # -------------------------------------------------
        # Resume validation
        # -------------------------------------------------

        if not resume_file:

            error = (
                "Please upload your resume PDF."
            )


            return render_template(

                "index.html",

                error=error,

                resume_text="",

                analysis_result=None,

                analysis_data=None,

                job_description=
                    job_description

            )


        if resume_file.filename == "":

            error = (
                "Please select a resume PDF."
            )


            return render_template(

                "index.html",

                error=error,

                resume_text="",

                analysis_result=None,

                analysis_data=None,

                job_description=
                    job_description

            )


        if not resume_file.filename.lower().endswith(
            ".pdf"
        ):

            error = (
                "Only PDF files are supported."
            )


            return render_template(

                "index.html",

                error=error,

                resume_text="",

                analysis_result=None,

                analysis_data=None,

                job_description=
                    job_description

            )


        # -------------------------------------------------
        # Save PDF
        # -------------------------------------------------

        filename = os.path.basename(
            resume_file.filename
        )


        pdf_path = os.path.join(

            app.config[
                "UPLOAD_FOLDER"
            ],

            filename

        )


        try:

            resume_file.save(
                pdf_path
            )

            print(
                "Resume saved:",
                pdf_path
            )


        except Exception as e:

            print(
                "File Save Error:",
                e
            )


            error = (
                "Could not save the resume."
            )


            return render_template(

                "index.html",

                error=error,

                resume_text="",

                analysis_result=None,

                analysis_data=None,

                job_description=
                    job_description

            )


        # -------------------------------------------------
        # Extract PDF text
        # -------------------------------------------------

        resume_text = extract_text_from_pdf(
            pdf_path
        )


        print(
            "Extracted text length:",
            len(resume_text)
        )


        if not resume_text:

            error = (
                "Could not extract text from this PDF. "
                "Please upload a text-based PDF resume."
            )


            return render_template(

                "index.html",

                error=error,

                resume_text="",

                analysis_result=None,

                analysis_data=None,

                job_description=
                    job_description

            )


        # =================================================
        # GEMINI
        # =================================================

        if client:

            analysis_result = gemini_analysis(

                resume_text,

                job_description

            )


        # =================================================
        # LOCAL FALLBACK
        # =================================================

        if analysis_result is None:

            print(
                "Using LOCAL FALLBACK ANALYSIS."
            )


            resume_analysis = (
                fallback_resume_analysis(
                    resume_text
                )
            )


            job_analysis = (
                fallback_job_match(

                    resume_text,

                    job_description

                )
            )


            analysis_result = (

                resume_analysis

                + "\n\n"

                + "## JOB MATCH ANALYSIS"

                + "\n\n"

                + job_analysis

            )


            error = (
                "Gemini AI is currently unavailable. "
                "Local ATS analysis is being used."
            )


        # =================================================
        # CONVERT TEXT TO DASHBOARD DATA
        # =================================================

        analysis_data = parse_analysis_result(
            analysis_result
        )


        # =================================================
        # SEND TO HTML
        # =================================================

        return render_template(

            "index.html",

            error=error,

            resume_text=resume_text,

            analysis_result=analysis_result,

            analysis_data=analysis_data,

            job_description=
                job_description

        )


    # =====================================================
    # GET
    # =====================================================

    return render_template(

        "index.html",

        error=None,

        resume_text="",

        analysis_result=None,

        analysis_data=None,

        job_description=""

    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return {

        "status": "running",

        "gemini_configured":
            client is not None,

        "primary_model":
            GEMINI_MODEL,

        "fallback_available":
            True

    }


# =========================================================
# RUN APPLICATION
# =========================================================
 
if __name__ == "__main__":

    print("=" * 60)
    print("AI RESUME ANALYZER")
    print("=" * 60)

    if GEMINI_API_KEY:
        print("Gemini API: CONFIGURED")
        print("AI mode: AVAILABLE")
    else:
        print("Gemini API: NOT CONFIGURED")
        print("AI mode: LOCAL FALLBACK")

    print("Primary Model:", GEMINI_MODEL)
    print("Fallback Analysis: ENABLED")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )