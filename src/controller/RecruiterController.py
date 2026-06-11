from typing import List, Dict, Any

class CandidateRanker:
    def __init__(self, config_weights: Dict[str, float] = None):
        # Set default weights safely
        self.weights = config_weights or {
            "skill_match": 0.50,
            "experience": 0.20,
            "cgpa": 0.15,
            "location": 0.10,
            "availability": 0.05
        }

    def _expand_weighted_skills(self, job_skills: List[Dict]) -> List[str]:
        expanded = []
        for item in job_skills:
            skill = str(item.get("skill", "")).strip().lower()
            weight = int(item.get("weight", 1))
            if skill:
                # Keep skills intact as complete strings (e.g., "machine learning")
                expanded.extend([skill] * weight)
        return expanded

    def _calculate_similarity(self, job_skills_expanded: List[str], candidate_skills: List[str]) -> float:
        if not job_skills_expanded:
            return 0.0
        
        # Lowercase candidate skills for case-insensitive matching
        c_skills_set = {s.lower().strip() for s in candidate_skills}
        
        # Count matches based on exact skill phrases rather than individual words
        matches = sum(1 for skill in job_skills_expanded if skill in c_skills_set)
        return matches / len(job_skills_expanded)

    def _get_location_score(self, c_loc: str, j_loc: str) -> float:
        if not j_loc or not c_loc:
            return 0.5
        return 1.0 if str(c_loc).strip().lower() == str(j_loc).strip().lower() else 0.4

    def _get_cgpa_score(self, cgpa: Any) -> float:
        try:
            val = float(cgpa)
            # Handle standard 4.0 scale vs 10.0 scale gently if needed, 
            # assuming 10.0 scale based on your original logic:
            if val > 10.0: 
                return 1.0
            return min(val / 10.0, 1.0)
        except (ValueError, TypeError):
            return 0.5

    def _get_experience_score(self, level: str) -> float:
        return {"Fresher": 0.6, "Experienced": 1.0}.get(level, 0.4)

    def _apply_filters(self, candidates: List[Dict], filters: Dict) -> List[Dict]:
        filtered = []
        min_cgpa = float(filters.get("minCgpa", 0))
        exp_levels = filters.get("experienceLevels", [])
        only_avail = filters.get("onlyAvailable", False)
        req_skills = [s.lower().strip() for s in filters.get("requiredSkills", [])]

        for c in candidates:
            try:
                if float(c.get("cgpa", 0)) < min_cgpa:
                    continue
            except (ValueError, TypeError):
                continue

            if exp_levels and c.get("experienceLevel") not in exp_levels:
                continue

            # If onlyAvailable is True, candidate must NOT be currently employed
            if only_avail and c.get("isCurrentlyEmployed", False):
                continue

            c_skills = [s.lower().strip() for s in c.get("skills", [])]
            if req_skills and not all(skill in c_skills for skill in req_skills):
                continue

            filtered.append(c)
        return filtered

    def rank(self, data: Dict[str, Any]) -> List[Dict]:
        candidates = data.get("candidates", [])
        filters = data.get("filters", {})
        job_skills = data.get("jobSkills", [])
        job_loc = data.get("jobLocation", "")

        # 1. Apply Hard Filters
        candidates = self._apply_filters(candidates, filters)
        if not candidates:
            return []

        # 2. Prepare Job Skills
        job_skills_expanded = self._expand_weighted_skills(job_skills)

        ranked_list = []
        for c in candidates:
            candidate_skills = c.get("skills", [])
            
            raw_scores = {
                "skill_match": self._calculate_similarity(job_skills_expanded, candidate_skills),
                "experience": self._get_experience_score(c.get("experienceLevel")),
                "cgpa": self._get_cgpa_score(c.get("cgpa")),
                "location": self._get_location_score(c.get("location"), job_loc),
                "availability": 1.0 if not c.get("isCurrentlyEmployed") else 0.3
            }

            final_score = sum(raw_scores[k] * self.weights.get(k, 0) for k in raw_scores)

            ranked_list.append({
                "studentId": c.get("id"),
                "finalScore": round(final_score * 100, 2),
                "breakdown": {k: round(v, 2) for k, v in raw_scores.items()}
            })

        return sorted(ranked_list, key=lambda x: x["finalScore"], reverse=True)