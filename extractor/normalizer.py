import re

from extractor.kb_lookup import KnowledgeBase


class SkillNormalizer:

    CLEAN_PATTERN = re.compile(
        r"[^\w\s#+./-]"
    )

    def __init__(self, kb: KnowledgeBase):

        self.kb = kb

    def clean_text(self, text: str) -> str:

        text = text.casefold().strip()

        return self.CLEAN_PATTERN.sub("", text)

    def normalize(self, entity: str):

        entity = self.clean_text(entity)

        return self.kb.resolve(entity)

    def normalize_list(self, entities):

        normalized = set()

        for entity in entities:

            skill = self.normalize(entity)

            if skill:

                normalized.add(skill)

        return normalized