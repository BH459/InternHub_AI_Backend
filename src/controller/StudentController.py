from typing import List, Dict, Any

class InternshipRecommender:
    def __init__(self):
        # Weights for the recommendation engine
        self.weights = {
            "skill_match": 0.45,
            "location_match": 0.30,
            "interest_match": 0.15,
            "experience_match": 0.10
        }

    def _calculate_skill_match(self, student_skills: List[str], required_skills: List[str]) -> float:
        if not required_skills:
            return 1.0  # If internship requires no specific skills, it's a perfect match for anyone
        
        s_skills_lower = {s.lower().strip() for s in student_skills}
        r_skills_lower = {r.lower().strip() for r in required_skills}
        
        matches = len(s_skills_lower.intersection(r_skills_lower))
        return matches / len(r_skills_lower)

    def _calculate_location_match(self, student_loc: str, intern_city: str, work_mode: str) -> float:
        # Remote work is highly accessible for rural/remote students
        if work_mode.lower() == "remote":
            return 1.0
            
        student_loc = str(student_loc).lower().strip()
        intern_city = str(intern_city).lower().strip()
        
        if student_loc == intern_city:
            return 1.0
        elif work_mode.lower() == "hybrid":
            return 0.6 # Partial score, might require some commute
        return 0.2 # Low score for required relocation

    def _calculate_interest_match(self, student_interests: List[str], company_industry: str) -> float:
        if not company_industry:
            return 0.5
            
        s_interests_lower = {i.lower().strip() for i in student_interests}
        c_industry_lower = str(company_industry).lower().strip()
        
        return 1.0 if c_industry_lower in s_interests_lower else 0.3

    def _calculate_experience_match(self, student_exp: str, required_exp: str) -> float:
        student_exp = str(student_exp).lower()
        required_exp = str(required_exp).lower()
        
        if required_exp == "fresher" or student_exp == "experienced":
            return 1.0 # Experienced students can do fresher roles, freshers can do fresher roles
        if student_exp == "fresher" and required_exp == "experienced":
            return 0.2 # Freshers shouldn't usually be recommended experienced roles
        return 0.5

    def recommend(self, payload: Dict[str, Any]) -> List[Dict]:
        student = payload.get("student", {})
        internships = payload.get("internships", [])
        
        # Extract Student details safely based on your provided schema
        profile = student.get("profile", {})
        compliance = student.get("compliance", {})
        
        student_skills = profile.get("skills", [])
        student_interests = profile.get("interests", [])
        student_exp = profile.get("experienceLevel", "Fresher")
        student_loc = compliance.get("location", "")
        
        # Skip internships the student has already applied to
        applied_internship_ids = [
            str(app.get("internshipId")) for app in student.get("appliedInternships", [])
        ]

        scored_internships = []

        for internship in internships:
            # Filter out expired or already applied internships
            if internship.get("status") != "Active":
                continue
            if str(internship.get("_id")) in applied_internship_ids:
                continue

            company = internship.get("company", {})
            location = internship.get("location", {})
            requirements = internship.get("requirements", {})

            # Calculate raw scores
            scores = {
                "skill_match": self._calculate_skill_match(
                    student_skills, internship.get("requiredSkills", [])
                ),
                "location_match": self._calculate_location_match(
                    student_loc, location.get("city", ""), location.get("workMode", "In-Office")
                ),
                "interest_match": self._calculate_interest_match(
                    student_interests, company.get("industry", "")
                ),
                "experience_match": self._calculate_experience_match(
                    student_exp, requirements.get("experiencedRequired", "Fresher")
                )
            }

            # Calculate final weighted score
            final_score = sum(scores[k] * self.weights[k] for k in scores)

            # Build a lightweight "Card" response for the frontend (Minimal text)
            scored_internships.append({
                "internshipId": internship.get("id"),
                "title": internship.get("title"),
                "companyName": company.get("name"),
                "companyLogoUrl": company.get("logoUrl"),
                "workMode": location.get("workMode"),
                "city": location.get("city"),
                "stipend": f"{internship.get('compensation', {}).get('stipendAmount', 0)} {internship.get('compensation', {}).get('currency', 'INR')}",
                "matchPercentage": round(final_score * 100),
                "tags": internship.get("requiredSkills", [])[:3] # Only send top 3 skills to avoid UI clutter
            })

        # Sort by best match and return top 5
        scored_internships.sort(key=lambda x: x["matchPercentage"], reverse=True)
        return scored_internships[:5]