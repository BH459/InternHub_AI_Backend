from pydantic import BaseModel
from typing import List, Dict


class SystemWeights(BaseModel):
    skill_match: float
    experience: float
    cgpa: float
    location: float
    availability: float


class Config(BaseModel):
    systemWeights: SystemWeights


class JobSkill(BaseModel):
    skill: str
    weight: int


class Filters(BaseModel):
    minCgpa: float
    experienceLevels: List[str]
    onlyAvailable: bool
    requiredSkills: List[str]


class Candidate(BaseModel):
    id: int
    skills: List[str]
    cgpa: float
    experienceLevel: str
    location: str
    isCurrentlyEmployed: bool


class RecruiterRankRequest(BaseModel):
    config: Config
    jobSkills: List[JobSkill]
    jobLocation: str
    filters: Filters
    candidates: List[Candidate]