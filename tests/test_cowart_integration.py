import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CowartIntegrationTests(unittest.TestCase):
    def test_codex_plugin_manifest_exposes_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "agent-sprite-forge")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("Cowart canvas handoff", manifest["interface"]["capabilities"])

    def test_portable_plugin_manifest_matches_codex_manifest(self):
        portable = json.loads((ROOT / "plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(portable["name"], codex["name"])
        self.assertEqual(portable["version"], codex["version"])
        self.assertEqual(portable["repository"], codex["repository"])

    def test_git_marketplace_points_to_repository_root(self):
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "agent-sprite-forge")
        self.assertEqual(entry["source"], {"source": "local", "path": "."})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")

    def test_bridge_skill_uses_supported_cowart_tools_and_preserves_bundles(self):
        skill = (ROOT / "skills" / "cowart-game-assets" / "SKILL.md").read_text()
        for tool_name in (
            "render_cowart_canvas_widget",
            "get_cowart_selection",
            "insert_cowart_image",
        ):
            self.assertIn(tool_name, skill)
        self.assertIn("artifacts/agent-sprite-forge/<asset-slug>/", skill)
        self.assertIn("Never stretch or crop a runtime sheet", skill)
        self.assertIn("replaceAiImageHolder", skill)
        self.assertIn("dryRun: true", skill)
        self.assertIn("Use PNG for reliable canvas handoff", skill)

    def test_map_and_sprite_skills_trigger_for_cowart(self):
        for skill_name in ("generate2dmap", "generate2dsprite"):
            skill = (ROOT / "skills" / skill_name / "SKILL.md").read_text()
            frontmatter = skill.split("---", 2)[1]
            self.assertIn("Cowart", frontmatter)
            self.assertIn("$agent-sprite-forge:cowart-game-assets", skill)


if __name__ == "__main__":
    unittest.main()
