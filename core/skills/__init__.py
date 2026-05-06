"""Skills Plugin System - Pluggable capability modules."""

from typing import Any, Optional
from pydantic import BaseModel
from pathlib import Path
import yaml


class SkillManifest(BaseModel):
    name: str
    version: str
    description: str
    author: Optional[str] = None
    instructions: str
    tools: list[str] = []
    config: dict[str, Any] = {}


class Skill:
    def __init__(self, manifest: SkillManifest, base_path: Path):
        self.manifest = manifest
        self.base_path = base_path

    @property
    def name(self) -> str:
        return self.manifest.name

    def get_instructions(self) -> str:
        return self.manifest.instructions


class SkillRegistry:
    def __init__(self, skills_dir: str = "./skills"):
        self._skills_dir = Path(skills_dir)
        self._skills: dict[str, Skill] = {}

    def discover(self):
        if not self._skills_dir.exists():
            return
        for skill_dir in self._skills_dir.iterdir():
            if skill_dir.is_dir():
                manifest_file = skill_dir / "skill.yaml"
                if manifest_file.exists():
                    manifest = SkillManifest(**yaml.safe_load(manifest_file.read_text()))
                    self._skills[manifest.name] = Skill(manifest, skill_dir)

    def register(self, name: str, instructions: str, tools: list[str] | None = None):
        manifest = SkillManifest(
            name=name,
            version="0.1.0",
            description="Custom skill",
            instructions=instructions,
            tools=tools or [],
        )
        self._skills[name] = Skill(manifest, self._skills_dir / name)

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_all(self) -> list[SkillManifest]:
        return [s.manifest for s in self._skills.values()]

    def remove(self, name: str):
        self._skills.pop(name, None)
