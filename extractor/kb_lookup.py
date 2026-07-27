from pathlib import Path
import pandas as pd
from collections import defaultdict

class KnowledgeBase:
    """
    Loads and provides access to the Career Lens Knowledge Base.
    """

    def __init__(self, kb_path: str = "knowledge_base"):

        self.kb_path = Path(kb_path)

        # DataFrames
        self.skills = pd.DataFrame()
        self.aliases = pd.DataFrame()
        self.categories = pd.DataFrame()
        self.inference_rules = pd.DataFrame()
        self.resources = pd.DataFrame()
        self.concept_hierarchy = pd.DataFrame()

        # Text files
        self.stopwords = set()

        # Lookup dictionaries
        self.skill_lookup = {}
        self.alias_lookup = {}
        self.category_lookup = {}
        self.concept_lookup = {}
        self.resource_lookup = {}
        self.canonical_lookup = {}
        self.reverse_alias = defaultdict(set)
        self.skill_category = {}
        self.inference_graph = defaultdict(lambda: defaultdict(set))
        self.load()

    def load(self):
        """Load all knowledge base files."""

        self.skills = pd.read_csv(self.kb_path / "skills.csv")

        self.aliases = pd.read_csv(self.kb_path / "aliases.csv")

        self.categories = pd.read_csv(self.kb_path / "categories.csv")

        self.inference_rules = pd.read_csv(
            self.kb_path / "inference_rules.csv"
        )
        self.concept_hierarchy = pd.read_csv(
            self.kb_path / "concept_hierarchy.csv"
        )
        resources = self.kb_path / "resources.csv"
        if resources.exists():
            self.resources = pd.read_csv(resources)

        stopword_file = self.kb_path / "stopwords.txt"

        with open(stopword_file, encoding="utf-8") as f:
            self.stopwords = {
                line.strip().casefold()
                for line in f
                if line.strip()
            }

        self._build_indexes()

    def _build_indexes(self):
        """Build fast lookup dictionaries."""

        self.skill_lookup = {
            row["skill_name"].casefold(): row["skill_id"]
            for _, row in self.skills.iterrows()
        }

        self.alias_lookup = {
            row["alias"].casefold(): row["skill_id"]
            for _, row in self.aliases.iterrows()
        }

        self.category_lookup = {
            row["category_id"]: row["category_name"]
            for _, row in self.categories.iterrows()
        }

        for _, row in self.concept_hierarchy.iterrows():
            child = row["child_skill"].casefold()
            parent = row["parent_concept"]
            self.concept_lookup.setdefault(child, set()).add(parent)

        for _, row in self.inference_rules.iterrows():
            trigger = row["trigger_skill"].casefold()
            relation = row["relation"].casefold()
            target = row["inferred_skill"]
            self.inference_graph[trigger][relation].add(target)

        for _, row in self.aliases.iterrows():
            self.reverse_alias[row["skill_id"]].add(row["alias"])

        for _, row in self.skills.iterrows():
            self.skill_category[row["skill_id"]] = row["category_id"]
            skill = str(row["skill_name"]).strip()
            self.canonical_lookup[skill.casefold()] = skill
        for _, row in self.aliases.iterrows():
            alias = str(row["alias"]).strip()
            skill = self.get_skill_name(row["skill_id"])
            self.canonical_lookup[alias.casefold()] = skill

        for _, row in self.resources.iterrows():
            self.resource_lookup[row["skill_id"]] = {
                "url": row["url"],
                "type": row["type"],
            }

    def get_skill_id(self, skill_name: str):
        return self.skill_lookup.get(skill_name.casefold())
    
    def get_skill_name(self, skill_id: str):
        result = self.skills.loc[
            self.skills["skill_id"] == skill_id
        ]

        if result.empty:
            return None

        return result.iloc[0]["skill_name"]
    def get_alias(self, alias: str):
        return self.alias_lookup.get(alias.casefold())
    def get_category(self, category_id: str):
        return self.category_lookup.get(category_id)
    def is_stopword(self, word: str):
        return word.casefold() in self.stopwords
    def skill_exists(self, skill_name: str):
        return skill_name.casefold() in self.skill_lookup
    def get_skill_category(self, skill):
        skill_id = self.get_skill_id(skill)
        category_id = self.skill_category.get(skill_id)
        return self.category_lookup.get(category_id)
    def get_resource(self, skill):
        skill_id = self.get_skill_id(skill)
        return self.resource_lookup.get(skill_id)
    def resolve(self, text):
        text = text.strip().casefold()
        if text in self.stopwords:
            return None
        return self.canonical_lookup.get(text)

      