# InternHub AI Backend

This FastAPI service provides deterministic matching for InternHub. It has no external AI-model or AI-provider integration: recommendations and rankings are computed locally with weighted rules over payloads supplied by the Express backend.

## AI features

- Ranks up to five active internships for a student by skill, location/work mode, industry interest, and experience level.
- Filters recruiter candidates by CGPA, experience level, availability, and required skills, then ranks them by weighted skill, experience, CGPA, location, and availability scores.
- Allows the recruiter-ranking request to supply system weights.

## Stack and layout

Python 3.13.1 is recorded by the existing virtual environment. Dependencies are FastAPI and Uvicorn.

```text
main.py                         # FastAPI app and router mounting
requirements.txt                # fastapi, uvicorn
src/
  routes/StudentRoutes.py       # POST /student/recommendations
  routes/RecruiterRoutes.py     # POST /recruiter/rank
  controller/StudentController.py   # InternshipRecommender rules
  controller/RecruiterController.py # CandidateRanker rules
  models/student.py             # Pydantic recommendation payload
  models/recruiter.py           # Pydantic ranking payload
```

## Installation and commands

```bash
cd AI_Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
uvicorn main:app --reload
```

The repository does not define environment variables, an `.env` file, a packaging configuration, test suite, or a production process command. For production, run Uvicorn with an explicit host and port appropriate to the host environment, for example:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Configure the main backend's `AI_BACKEND` value to this service's base URL. Keep this service reachable only from the backend/network that needs it; it does not implement authentication or CORS configuration.

## Endpoints and contracts

| Method | Endpoint | Request | Response |
| --- | --- | --- | --- |
| `GET` | `/` | none | `{ "message": "FastAPI Server Running" }` |
| `POST` | `/student/recommendations` | student profile/compliance plus internships | success flag, student name, result count, and recommendations |
| `POST` | `/recruiter/rank` | ranking config, job skills/location, filters, and candidates | success flag, input count, passed-filter count, and ranking |

Student requests require `student.name`, `profile.skills`, `profile.interests`, `profile.experienceLevel`, `compliance.location`, and internship fields including ID, status, skills, company, location, compensation, and requirements. Recommendations include `internshipId`, title, company details, work mode, city, stipend, `matchPercentage`, and up to three skill tags.

Recruiter requests require `config.systemWeights`, weighted `jobSkills`, `jobLocation`, `filters`, and `candidates`. Ranking results contain each `studentId`, `finalScore`, and a score `breakdown`. Pydantic validates incoming payload types; invalid shapes receive FastAPI validation responses.

## Actual request flow

```text
Frontend
  → Express backend (cookie-authenticated route)
  → FastAPI AI backend (internal HTTP request via AI_BACKEND)
  → local weighted rule engine
  → FastAPI response
  → Express response
  → Frontend
```

For student recommendations, Express reads the logged-in student's profile and active internships before calling FastAPI. For recruiter ranking, it verifies ownership of the internship, reads its applicants, and builds the candidate payload. Thus the AI backend neither accesses PostgreSQL nor authenticates the frontend directly.
