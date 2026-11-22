import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.database import Base, engine, get_db
from app.models.models import *
from app.schemas import *

SECRET = os.getenv("JWT_SECRET", "career-os-development-secret")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

app = FastAPI(title="CareerOS API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

Base.metadata.create_all(bind=engine)


def seed_jobs(db: Session):
    if db.scalar(select(Job).limit(1)):
        return
    jobs = [
        ("ext-1", "Northstar Labs", "Backend Engineer Intern", "Build Python APIs, distributed services, Kafka pipelines and AI infrastructure.", "Bangalore, India", "Internship", 2, "Python, FastAPI, Kafka, PostgreSQL"),
        ("ext-2", "CloudForge", "Python Backend Developer", "Develop REST APIs, SQL databases, Celery workers and containerized microservices.", "Remote", "Full-time", 4, "Python, FastAPI, SQLAlchemy, Docker"),
        ("ext-3", "VectorWorks", "AI Platform Engineer", "Create LLM agents, vector search pipelines, RAG systems and evaluation tooling.", "Hyderabad, India", "Full-time", 5, "Python, LangGraph, Qdrant, LLM"),
        ("ext-4", "DataRelay", "Data Engineer", "Build streaming data platforms using Kafka, Python and cloud infrastructure.", "Pune, India", "Full-time", 6, "Python, Kafka, SQL, AWS"),
        ("ext-5", "Fintech Horizon", "Full Stack Developer", "Build React dashboards and FastAPI services for financial workflows.", "Remote", "Full-time", 4, "React, JavaScript, FastAPI, PostgreSQL"),
    ]
    for external_id, company, title, desc, loc, type_, exp, skills in jobs:
        db.add(Job(external_id=external_id, company=company, title=title, description=desc, location=loc,
                   employment_type=type_, experience_max=exp, skills=skills, status="active"))
    db.commit()


@app.on_event("startup")
def startup():
    db = next(get_db())
    seed_jobs(db)


def create_token(user_id: int):
    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try:
        user_id = int(jwt.decode(credentials.credentials, SECRET, algorithms=[ALGORITHM])["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "CareerOS"}


@app.post("/api/v1/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "Email already registered")
    user = User(email=payload.email, password_hash=pwd_context.hash(payload.password), full_name=payload.full_name)
    db.add(user)
    db.flush()
    profile = CandidateProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    return {"access_token": create_token(user.id), "token_type": "bearer", "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user.id), "token_type": "bearer", "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}


@app.get("/api/v1/candidates/me")
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    return {"id": profile.id, "headline": profile.headline, "summary": profile.summary, "skills": profile.skills,
            "location": profile.location, "target_role": profile.target_role}


@app.put("/api/v1/candidates/me")
def update_profile(payload: ProfileRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    return {"ok": True}


@app.post("/api/v1/candidates/resume")
async def upload_resume(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    if not text.strip():
        raise HTTPException(400, "Resume file is empty")
    known = ["Python", "FastAPI", "React", "JavaScript", "SQL", "PostgreSQL", "Kafka", "Docker", "AWS", "LangGraph", "Qdrant"]
    found = [skill for skill in known if skill.lower() in text.lower()]
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile.resume_text = text[:50000]
    profile.skills = ", ".join(found)
    db.commit()
    return {"filename": file.filename, "extracted_skills": found, "facts": [{"source": "resume_text", "supported": True}]}


@app.get("/api/v1/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return [{"id": j.id, "company": j.company, "title": j.title, "location": j.location,
             "employment_type": j.employment_type, "skills": j.skills, "salary": j.salary,
             "description": j.description} for j in db.scalars(select(Job).where(Job.status == "active"))]


@app.post("/api/v1/jobs/search")
def search_jobs(payload: SearchRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    jobs = db.scalars(select(Job).where(Job.status == "active")).all()
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    candidate_skills = {s.strip().lower() for s in (profile.skills or "").split(",")}
    hay = payload.query.lower()
    results = []
    for job in jobs:
        job_skills = {s.strip().lower() for s in job.skills.split(",")}
        skill_overlap = len(candidate_skills & job_skills)
        lexical = sum(1 for word in hay.split() if word in (job.title + " " + job.description).lower()) if hay else 0
        if payload.location and payload.location.lower() not in job.location.lower(): continue
        if payload.employment_type and payload.employment_type.lower() not in job.employment_type.lower(): continue
        score = round(min(0.99, 0.25 + skill_overlap * 0.12 + lexical * 0.08), 2)
        if hay and lexical == 0 and skill_overlap == 0: continue
        matched = sorted(candidate_skills & job_skills)
        results.append({"id": job.id, "company": job.company, "title": job.title, "location": job.location,
                        "employment_type": job.employment_type, "skills": job.skills, "salary": job.salary,
                        "description": job.description, "score": score,
                        "explanation": f"{len(matched)} candidate skills match: {', '.join(matched) if matched else 'role and profile relevance'}"})
    results.sort(key=lambda item: item["score"], reverse=True)
    return results


@app.get("/api/v1/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    payload = SearchRequest(query="")
    # Shared ranking behavior without exposing search request details.
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    target = (profile.target_role or profile.headline).lower()
    candidate_skills = {s.strip().lower() for s in (profile.skills or "").split(",")}
    output = []
    for job in db.scalars(select(Job).where(Job.status == "active")):
        job_skills = {s.strip().lower() for s in job.skills.split(",")}
        overlap = len(candidate_skills & job_skills)
        role_match = 0.15 if target and target in job.title.lower() else 0
        score = round(min(0.99, 0.35 + overlap * 0.12 + role_match), 2)
        output.append({"id": job.id, "company": job.company, "title": job.title, "location": job.location,
                       "employment_type": job.employment_type, "skills": job.skills, "score": score,
                       "explanation": f"Role fit plus {overlap} matching skills"})
    return sorted(output, key=lambda x: x["score"], reverse=True)[:5]


@app.post("/api/v1/recommendations/feedback")
def feedback(payload: FeedbackRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    db.add(CandidateMemory(candidate_id=profile.id, category="interaction", key="feedback", value=f"{payload.job_id}:{payload.feedback}", confirmed=1))
    db.commit()
    return {"ok": True}


@app.post("/api/v1/agent/chat")
def agent_chat(payload: AgentRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    message = payload.message.lower()
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    if "preference" in message or "location" in message:
        response = f"I remember your location as {profile.location or 'not set'} and target role as {profile.target_role or 'not set'}."
    elif "resume" in message:
        response = f"Your resume profile has {len(profile.skills.split(',')) if profile.skills else 0} extracted skills."
    else:
        response = "I can search jobs, explain matches, update preferences, save jobs, or tailor a resume. Tell me a role and location."
    return {"response": response, "tools_used": ["get_candidate_profile"] if profile else []}


@app.post("/api/v1/applications")
def create_application(payload: ApplicationRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    app_row = Application(candidate_id=profile.id, job_id=payload.job_id, status="SAVED")
    db.add(app_row)
    db.commit()
    return {"id": app_row.id, "job_id": app_row.job_id, "status": app_row.status}


@app.get("/api/v1/applications")
def get_applications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    rows = db.scalars(select(Application).where(Application.candidate_id == profile.id)).all()
    result = []
    for row in rows:
        job = db.get(Job, row.job_id)
        result.append({"id": row.id, "status": row.status, "job": {"id": job.id, "title": job.title, "company": job.company}})
    return result


@app.patch("/api/v1/applications/{application_id}")
def update_application(application_id: int, payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    allowed = {"DISCOVERED", "SAVED", "APPLIED", "INTERVIEW", "OFFER", "REJECTED"}
    status = str(payload.get("status", "")).upper()
    if status not in allowed:
        raise HTTPException(422, "Invalid application state")
    row = db.get(Application, application_id)
    if not row:
        raise HTTPException(404, "Application not found")
    row.status = status
    db.commit()
    return {"id": row.id, "status": row.status}


@app.get("/api/v1/candidates/preferences")
def get_preferences(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    rows = db.scalars(select(CandidatePreference).where(CandidatePreference.profile_id == profile.id)).all()
    return [{"id": r.id, "key": r.key, "value": r.value, "confirmed": bool(r.confirmed)} for r in rows]


@app.put("/api/v1/candidates/preferences")
def update_preferences(payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    for key, value in payload.items():
        existing = db.scalar(select(CandidatePreference).where(CandidatePreference.profile_id == profile.id, CandidatePreference.key == key))
        if existing:
            existing.value = str(value)
        else:
            db.add(CandidatePreference(profile_id=profile.id, key=key, value=str(value), confirmed=1))
    db.commit()
    return {"ok": True}


@app.post("/api/v1/resumes/tailor")
def tailor_resume(payload: dict, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    job = db.get(Job, int(payload.get("job_id", 0)))
    if not job:
        raise HTTPException(404, "Job not found")
    skills = [s.strip() for s in (profile.skills or "").split(",") if s.strip()]
    relevant = [s for s in skills if s.lower() in (job.skills + " " + job.description).lower()]
    summary = f"Professional summary: {profile.summary or ('Candidate with evidence in ' + ', '.join(relevant))}."
    return {"job": job.title, "summary": summary, "highlighted_skills": relevant,
            "draft": f"{summary}\n\nRelevant evidence:\n" + "\n".join(f"- {skill}" for skill in relevant),
            "approval_required": True}


@app.get("/api/v1/agent/conversations")
def conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    return db.scalars(select(Conversation).where(Conversation.candidate_id == profile.id)).all()


@app.get("/api/v1/agent/memory")
def memory(user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    rows = db.scalars(select(CandidateMemory).where(CandidateMemory.candidate_id == profile.id)).all()
    return [{"category": r.category, "key": r.key, "value": r.value, "confirmed": bool(r.confirmed)} for r in rows]
