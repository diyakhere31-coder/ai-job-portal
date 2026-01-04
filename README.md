# 🤖 AI Job Portal (Django + NLP)

An intelligent job portal built using **Django** that automates resume screening using **NLP, weighted skill scoring, and domain-aware AI logic**.  
The platform supports **IT, Mechanical, and Civil** job domains with recruiter, admin, and user dashboards.

---

## 🚀 Key Features

- 🔍 AI-based Resume Screening & Match Scoring
- 🧠 NLP + TF-IDF + Cosine Similarity
- 🏢 Recruiter Dashboard with Job Analytics
- 👨‍💼 Admin Panel with User & Job Insights
- 👩‍💻 User Job Search & Application Tracking
- 📊 Visual analytics (charts & stats)
- 🔐 Role-based authentication (Admin / Recruiter / User)

---

## 🖥️ Screenshots

## 🏠 Home Page
![Home Page](Screenshots/home.png)

## 👩🏻‍💻 IT Job Listings
![IT Jobs](Screenshots/IT_jobs.png)

## 👨🏼‍🔧 Mechanical Job Listings
![Mechanical Jobs](Screenshots/Mechanical_jobs.png)

## 👨🏼‍🔧 Civil Job Listings
![Civil Jobs](Screenshots/Civil_jobs.png)

## 📝 Post a Job
![Post Job](Screenshots/Post_new_job.png)

## 👔 Recruiter Dashboard
![Recruiter Dashboard](Screenshots/Recruiter_dashboard.png)

## 🧠 AI Resume Screening
![AI Screening](Screenshots/AI_screening.png)

## 🛠 Admin Dashboard
![Admin Dashboard](Screenshots/Admin_dashboard_charts.png)

---

## 🧠 AI Matching Logic (Overview)

- Skill extraction using predefined skill sets
- Weighted primary skills per domain
- Resume–Job similarity using **TF-IDF + Cosine Similarity**
- Domain penalty to avoid false positives
- Final score with smart thresholding

---

## ⚙️ Tech Stack

- **Backend:** Django, Python
- **AI / NLP:** scikit-learn, TF-IDF, Cosine Similarity
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (development)
- **Charts:** Chart.js

---

## 🔒 Security & Privacy

- Resumes and user data are **NOT committed**
- `.gitignore` protects:
  - `db.sqlite3`
  - `media/`
  - uploaded resumes
  - environment files

---

## 📌 Future Enhancements

- Resume keyword heatmaps
- Job recommendation engine
- Resume parsing with spaCy
- Deployment (Docker / AWS)

---

## 👩‍💻 Author

**Diya Khere**  
Aspiring Software Developer | Django | AI-Driven Systems
