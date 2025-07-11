# 🧠 **AI Interview & Scoring System**

An AI-powered system that conducts structured interviews and scores responses using NLP and machine learning. Built for **HR screening** and **academic admissions** at **KSBL**.

---

## 🚀 **Features**

- 💬 **Interactive chatbot** that asks domain-specific questions (HR or Academic)
- 🤖 **LLM-based scoring** using Hugging Face's **RoBERTa**
- 📊 **Admin dashboard** (React) to view scores, filter results, and gain insights
- 🔐 **Login system** for candidates and admins
- 🗃️ **PostgreSQL backend** to store interviews and results

---

## 🛠️ **Tech Stack**

| **Layer**        | **Technology**                |
|------------------|-------------------------------|
| Frontend         | React + Tailwind CSS          |
| Backend API      | FastAPI (Python)              |
| NLP Engine       | Hugging Face (RoBERTa)        |
| Database         | PostgreSQL                    |
| Authentication   | JWT or Session-based login    |

---

## 📁 **Project Architecture**


interview-system/
├── backend/              
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── scoring/
│   └── requirements.txt
├── frontend/           
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
├── docs/                 
│   └── AI_Interview_Scoring_System_BRD.pdf
└── README.md


---

## ⚙️ **Getting Started**

### 1. **Clone the Repository**

```bash
git clone https://github.com/your-username/ai-interview-chatbot.git
cd ai-interview-chatbot
```

### 2. **Setup Backend**
```bash
cd backend
python -m venv env
source env/bin/activate        # On Windows: .\env\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. **Setup Frontend**
```bash
cd frontend
npm install
npm start
```

## **How It Works**
- The chatbot asks structured interview questions from a predefined set
- The candidate's responses are passed to the LLM model (RoBERTa) for scoring
- Scores and responses are stored in PostgreSQL
- An admin dashboard allows reviewers to view, compare, and filter candidate results


## **Data Flow**
Candidate → Chatbot (React) → FastAPI (API) → Scoring Engine → PostgreSQL → Admin Dashboard

## **Documentation**
[Business Requirements Document (BRD)](docs/AI_Interview_Scoring_System_BRD.pdf)


## **Capstone Proposal Summary**

**To-Do / Upcoming**
 - Voice input for chatbot (Web Speech API or Python STT)
 - Camera integration (MediaRecorder + React)
 - Admin role-based access
 - Scoring explainability

**Developed By**

Wardah Khan

Sanya Afzal Makba

Advisor: Dr. Rizwan Tanweer, KSBL
