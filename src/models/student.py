from pydantic import BaseModel
from typing import List


class StudentProfile(BaseModel):
    skills: List[str]
    interests: List[str]
    experienceLevel: str


class StudentCompliance(BaseModel):
    location: str


class Student(BaseModel):
    name: str
    profile: StudentProfile
    compliance: StudentCompliance


class Company(BaseModel):
    name: str
    industry: str


class InternshipLocation(BaseModel):
    city: str
    workMode: str


class Compensation(BaseModel):
    stipendAmount: int
    currency: str


class Requirements(BaseModel):
    experiencedRequired: str


class Internship(BaseModel):
    id: str
    status: str
    title: str
    company: Company
    requiredSkills: List[str]
    location: InternshipLocation
    compensation: Compensation
    requirements: Requirements


class InternshipRecommendationRequest(BaseModel):
    student: Student
    internships: List[Internship]