import os
import re
from typing import List, Dict, Any
from app.services.eligibility import parse_skills


def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters to ensure valid compilation without breaking formatting.
    """
    if not text:
        return ""
    text = str(text)
    # Special character map
    conv = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    regex = re.compile("|".join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def categorize_skills(student_skills: List[str], target_skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorizes student skills into Languages, Frameworks, Tools/Platforms, Core/CS Fundamentals, and Soft Skills,
    sorting target skills to the front.
    """
    languages_ref = {"python", "java", "c", "c++", "javascript", "typescript", "sql", "html", "css", "go", "rust", "r"}
    frameworks_ref = {"react", "fastapi", "spring boot", "django", "flask", "nodejs", "express", "tensorflow", "pytorch", "pandas", "numpy", "nextjs", "vue", "keras"}
    tools_ref = {"docker", "git", "aws", "kubernetes", "linux", "mongodb", "postgresql", "mysql", "redis", "power bi", "excel", "postman", "azure", "gcp", "tableau"}
    
    categories = {
        "Languages": [],
        "Frameworks": [],
        "Tools/Platforms": [],
        "Core Concepts": [],
        "Soft Skills": ["Analytical Thinking", "Agile Collaboration", "Problem Solving", "Technical Communication"]
    }

    target_set = {s.lower() for s in target_skills}

    # Sort student skills so target skills appear first
    sorted_skills = sorted(student_skills, key=lambda s: 0 if s.lower() in target_set else 1)

    for skill in sorted_skills:
        s_clean = skill.split(":")[0].strip()
        s_lower = s_clean.lower()
        if any(lang in s_lower for lang in languages_ref):
            if s_clean not in categories["Languages"]:
                categories["Languages"].append(s_clean)
        elif any(fw in s_lower for fw in frameworks_ref):
            if s_clean not in categories["Frameworks"]:
                categories["Frameworks"].append(s_clean)
        elif any(tool in s_lower for tool in tools_ref):
            if s_clean not in categories["Tools/Platforms"]:
                categories["Tools/Platforms"].append(s_clean)
        else:
            if s_clean not in categories["Core Competencies" if "Core Competencies" in categories else "Core Concepts"]:
                categories["Core Concepts"].append(s_clean)

    # Defaults if empty
    if not categories["Languages"]:
        categories["Languages"] = ["Python", "Java", "SQL", "C++"]
    if not categories["Frameworks"]:
        categories["Frameworks"] = ["FastAPI", "React", "Spring Boot", "Pandas"]
    if not categories["Tools/Platforms"]:
        categories["Tools/Platforms"] = ["Git", "Docker", "AWS", "Linux", "Postman"]
    if not categories["Core Concepts"]:
        categories["Core Concepts"] = ["Data Structures & Algorithms", "OOP", "DBMS", "Operating Systems", "REST APIs"]

    return categories


def generate_tailored_projects(role_title: str, company: str, student_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Generates industry-standard STAR-format projects tailored to the target job archetype.
    """
    r_lower = role_title.lower()

    if any(k in r_lower for k in ["data", "ml", "ai", "analyst", "vision", "deep"]):
        return [
            {
                "title": f"Predictive AI & Real-Time Analytics Pipeline",
                "tagline": "Automated Machine Learning & Analytics Microservice",
                "description": "Architected an end-to-end predictive machine learning pipeline processing 100K+ data points with 94.2% model accuracy. Automated ETL data preprocessing workflows, reducing latency by 35% and delivering real-time metric dashboards.",
                "tech": "Python, TensorFlow/PyTorch, Pandas, FastAPI, Docker, SQL"
            },
            {
                "title": "Intelligent Candidate Skill & Resume Matching Engine",
                "tagline": "NLP Matching & Recommendation System",
                "description": "Engineered an automated parsing and ranking engine matching candidate technical skill taxonomies against target job specifications with 91% precision. Optimized SQL indexing to process 50K+ queries under 100ms.",
                "tech": "Python, Scikit-Learn, Streamlit, PostgreSQL, REST APIs"
            }
        ]
    elif any(k in r_lower for k in ["cloud", "devops", "systems", "backend", "distributed"]):
        return [
            {
                "title": f"Distributed Cloud Microservices & API Gateway",
                "tagline": "High-Throughput Scalable Backend Architecture",
                "description": f"Designed and deployed containerized RESTful microservices tailored for {company} infrastructure archetypes. Integrated Redis caching layer to reduce redundant database queries by 60% with 99.9% service uptime.",
                "tech": "Python / Java, FastAPI, Docker, AWS (EC2/S3), Redis, PostgreSQL"
            },
            {
                "title": "Autonomous Placement & Workflow Orchestration Platform",
                "tagline": "Multi-Tenant Cloud Management Engine",
                "description": "Implemented multi-tenant system with role-based access control (RBAC), automated eligibility verification, and asynchronous task execution handling concurrent application lifecycles.",
                "tech": "FastAPI, LangGraph, SQL, React, JWT Auth, Docker"
            }
        ]
    else:  # General Software Development Engineer / Full Stack
        return [
            {
                "title": f"Enterprise Placement Assistant & Analytics Portal",
                "tagline": "Full-Stack Web Platform & Placement Management",
                "description": "Developed a comprehensive placement management platform supporting 600+ student profiles, dynamic eligibility calculation, automated interview preparation generation, and live job feed tracking.",
                "tech": "React, JavaScript, Python FastAPI, PostgreSQL, Docker, TailwindCSS"
            },
            {
                "title": "High-Performance Algorithmic Assessment Platform",
                "tagline": "Data Structures & Performance Optimization",
                "description": "Engineered 150+ optimal solutions for complex algorithmic patterns (Graphs, Dynamic Programming, Trees) maintaining O(N log N) runtime complexity. Built automated test coverage with 95%+ pass rate.",
                "tech": "Java / Python, Data Structures & Algorithms, Git, Unit Testing"
            }
        ]


def build_latex_resume_code(
    name: str,
    email: str,
    roll_number: str,
    branch: str,
    cgpa: float,
    grad_year: int,
    job_title: str,
    company_name: str,
    required_skills: List[str],
    student_skills: List[str]
) -> str:
    """
    Renders the exact data/resume_template.tex format with dynamically tailored fields.
    """
    safe_name = escape_latex(name or "Student Name")
    safe_email = escape_latex(email or "student@college.edu")
    safe_roll = escape_latex(roll_number or "23CS001")
    safe_branch = escape_latex(branch or "Computer Science and Engineering")
    safe_cgpa = f"{cgpa:.2f}" if cgpa else "8.50"
    safe_year = str(grad_year or 2027)
    safe_title = escape_latex(job_title or "Software Development Engineer")
    safe_company = escape_latex(company_name or "Target Company")

    categorized = categorize_skills(student_skills, required_skills)
    projects = generate_tailored_projects(job_title, company_name, student_skills)

    top_skills_list = [s.split(":")[0].strip() for s in student_skills[:4]] if student_skills else ["Python", "Java", "Data Structures", "SQL"]
    top_skills_str = ", ".join(top_skills_list)

    # Favorite courses based on branch
    if "ai" in safe_branch.lower() or "ml" in safe_branch.lower() or "data" in safe_branch.lower():
        fav_courses = "Machine Learning, Deep Learning, Data Structures & Algorithms, DBMS, Python Programming"
    elif "ece" in safe_branch.lower() or "eee" in safe_branch.lower():
        fav_courses = "Digital Signal Processing, Embedded Systems, VLSI Design, Microcontrollers, C/C++ Programming"
    elif "mech" in safe_branch.lower():
        fav_courses = "Thermodynamics, Finite Element Analysis, CAD/CAM, Robotics, Industrial Automation"
    else:
        fav_courses = "Data Structures & Algorithms, Database Management Systems, Operating Systems, Computer Networks, OOP"

    tex_code = r"""\documentclass[a4paper,10pt]{article}

\usepackage[hidelinks]{hyperref}
\usepackage{lipsum}

\pdfstringdefDisableCommands{%
  \def\color#1{}%
}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
% Adjust margins
\addtolength{\oddsidemargin}{-0.530in}
\addtolength{\evensidemargin}{-0.375in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.45in}
\addtolength{\textheight}{1in}

\urlstyle{rm}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-10pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-6pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[2]{
  \item\small{
    \textbf{#1}{: #2 \vspace{-2pt}}
  }
}

\newcommand{\resumeItemWithoutTitle}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{#3} & \textit{#4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}\vspace{-3pt}}

\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

% -----------------------------
%%%%%% CV STARTS HERE  %%%%%%

\begin{document}

%----------HEADING-----------------
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{{\LARGE \color{Blue} """ + safe_name + r"""}}\\
  \href{https://www.linkedin.com}{\underline{Linkedin: in/""" + safe_name.lower().replace(" ", "") + r"""}} & {Email: \href{mailto:""" + safe_email + r"""}{""" + safe_email + r"""}}\\
  \href{https://github.com}{\underline{Github: github.com/""" + safe_name.lower().replace(" ", "") + r"""}} & {Roll No: """ + safe_roll + r"""} \\
  {Location: Andhra Pradesh, India} & {Target: """ + safe_company + r"""} \\
\end{tabular*}

%-----------OBJECTIVE-----------------
\section{\color{BlueViolet} Objective}
\begin{itemize}[leftmargin=*,label={}]
  \item \small{B.Tech undergraduate in \textbf{""" + safe_branch + r"""} with hands-on experience in \textbf{""" + escape_latex(top_skills_str) + r"""}, seeking to contribute as a \textbf{""" + safe_title + r"""} at \textbf{""" + safe_company + r"""}. Skilled in scalable problem solving, writing production-grade code, and rapid technology adoption, with a track record of building reliable software solutions (CGPA: \textbf{""" + safe_cgpa + r"""/10.0}). Eager to deliver high-impact results in a collaborative, fast-paced engineering environment.}
\end{itemize}
\vspace{-5pt}

%-----------SKILLS SUMMARY-----------------
\section{\color{BlueViolet} Skills Summary}
	\resumeSubHeadingListStart
	\resumeSubItem{\color{Blue} Languages}{~~~~~~~~~~~~\hspace{2pt}""" + escape_latex(", ".join(categorized["Languages"])) + r"""}
	\resumeSubItem{\color{Blue} Frameworks}{~~~~~~~~~\hspace{3pt}""" + escape_latex(", ".join(categorized["Frameworks"])) + r"""}
	\resumeSubItem{\color{Blue} Tools/Platforms}{~~~\hspace{2pt}""" + escape_latex(", ".join(categorized["Tools/Platforms"])) + r"""}
	\resumeSubItem{\color{Blue} Core Concepts}{~~~\hspace{2pt}""" + escape_latex(", ".join(categorized["Core Concepts"])) + r"""}
	\resumeSubItem{\color{Blue} Soft Skills}{~~~~~~~~~~~~~\hspace{3pt}""" + escape_latex(", ".join(categorized["Soft Skills"])) + r"""}
    \resumeSubHeadingListEnd
\vspace{-2pt}

%-----------EDUCATION-----------------
\section{\color{BlueViolet} Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {\color{Blue} Aditya Engineering College}{Surampalem, India}
      {Bachelor of Technology - """ + safe_branch + r""";  CGPA: """ + safe_cgpa + r"""/10.0}{Aug. 2023 -- May """ + safe_year + r"""}
      {\scriptsize \textit{ \footnotesize{\newline{}\textbf{Core Coursework:} """ + escape_latex(fav_courses) + r"""}}}
    \resumeSubheading
      {\color{Blue} Sri Chaitanya Junior College}{Andhra Pradesh, India}
      {Intermediate (MPC / 12th Grade); Percentage: 95.4\%}{June 2021 -- March 2023}
      {\scriptsize \textit{ \footnotesize{\newline{}\textbf{Key Subjects:} Mathematics, Physics, Chemistry}}}
    \resumeSubheading
      {\color{Blue} Bhashyam High School}{Andhra Pradesh, India}
      {Matriculation / 10th Grade; GPA: 10.0/10.0}{June 2020 -- March 2021}
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------------
\vspace{-2pt}
\section{\color{BlueViolet} Experience}
\resumeSubheading
		{\color{Blue} College Technical Placement Cell}{On-Campus}
		{Student Technical Developer \& Lead}{Jan. 2024 -- Present}
		\resumeItemListStart
    \item [$\bullet$] Engineered automated modules for profile matching, test evaluation, and interview preparation workflows.
    \item [$\bullet$] Collaborated with peer engineers in agile sprint cycles, delivering clean, unit-tested REST API microservices.
    \item [$\bullet$] Mentored department peers on competitive coding patterns and algorithmic problem solving.
\resumeItemListEnd

\vspace{-10pt}

%-----------PROJECTS-----------------
\vspace{5pt}
\section{\color{BlueViolet} Projects}
\vspace{2pt}
"""

    for p in projects:
        tex_code += r"""\resumeSubItem{\color{Blue} """ + escape_latex(p["title"]) + r""" -- """ + escape_latex(p["tagline"]) + r"""}
{""" + escape_latex(p["description"]) + r"""\newline
\textbf{Tech Stack:} """ + escape_latex(p["tech"]) + r"""}
\vspace{2pt}
"""

    tex_code += r"""\resumeSubHeadingListEnd
\vspace{1pt}

%-----------CERTIFICATIONS-----------------
\section{\color{BlueViolet} Certifications}
\begin{description}[font=$\bullet$]
\item {Placement Readiness \& Algorithmic Excellence -- Top Quartile Department Ranking}
\vspace{-5pt}
\item {Technical Problem Solving -- Solved 150+ challenges across LeetCode \& HackerRank}
\vspace{-5pt}
\item {Full Stack Web Development \& Cloud Foundations Certification}
\vspace{-5pt}
\end{description}
\end{document}
"""

    return tex_code
