from typing import Iterable

from config import SKILLS


def calculate_score(job_text: str, skills: Iterable[str] | None = None) -> int:
	"""Return a percentage score based on how many skills appear in job_text.

	Score is an integer 0–100.
	"""

	text = job_text.lower()
	skill_list = list(skills) if skills is not None else list(SKILLS)
	if not skill_list:
		return 0

	matches = 0
	for skill in skill_list:
		if skill.lower() in text:
			matches += 1

	return int((matches / len(skill_list)) * 100)


