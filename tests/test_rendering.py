from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "alisha"


def load_alisha_module():
    loader = importlib.machinery.SourceFileLoader("alisha_script", str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


alisha = load_alisha_module()


class RenderingTests(unittest.TestCase):
    def test_markdown_and_blockquotes_are_split_into_panels(self) -> None:
        answer = "# Heading\n\nText\n\n> Note: boxed context\n\nMore text"

        segments = alisha.split_markdown_and_panels(answer)

        self.assertEqual(
            segments,
            [
                ("markdown", "# Heading\n\nText"),
                ("panel", "Note: boxed context"),
                ("markdown", "More text"),
            ],
        )

    def test_blockquotes_inside_code_fences_stay_markdown(self) -> None:
        answer = "```sh\nprintf '> not a quote'\n```\n\n> Tip: real quote"

        segments = alisha.split_markdown_and_panels(answer)

        self.assertEqual(
            segments,
            [
                ("markdown", "```sh\nprintf '> not a quote'\n```"),
                ("panel", "Tip: real quote"),
            ],
        )

    def test_panel_from_admonition_uses_matching_title(self) -> None:
        panel = alisha.panel_from_blockquote("Warning: destructive step")

        self.assertEqual(panel.title, " Warning ")
        self.assertEqual(panel.border_style, "alisha.panel.warning")


if __name__ == "__main__":
    unittest.main()
