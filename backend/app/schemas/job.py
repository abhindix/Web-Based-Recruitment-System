from pydantic import BaseModel

class JobCreate(BaseModel):
    role_title: str
    requirements: str
    indicative_salary: int | None = None

class JobOut(BaseModel):
    id: int
    role_title: str
    requirements: str
    indicative_salary: int | None
    hiring_manager_id: int

    class Config:
        from_attributes = True
