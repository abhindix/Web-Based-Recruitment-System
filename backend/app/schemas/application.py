from pydantic import BaseModel, EmailStr

class ApplicationCreate(BaseModel):
    job_id: int
    phone: str
    cover_letter: str

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    phone: str
    cover_letter: str

    class Config:
        from_attributes = True
