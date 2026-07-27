class SkillIdentifier:

    def __init__(self, kb):

        self.kb = kb
        self.lookup = kb.concept_lookup

    def expand(self, skills):

        expanded = set()

        for skill in skills:

            key = skill.casefold().strip()
            
            if key in self.lookup:
                expanded.update(self.lookup[key])
            else:
                expanded.add(skill)

        return expanded