from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileRequest(BaseModel):
    headline: str = ""
    summary: str = ""
    skills: str = ""
    location: str = ""
    target_role: str = ""


class SearchRequest(BaseModel):
    query: str = ""
    location: str = ""
    employment_type: str = ""


class FeedbackRequest(BaseModel):
    job_id: int
    feedback: str


class AgentRequest(BaseModel):
    message: str


class ApplicationRequest(BaseModel):
    job_id: int
