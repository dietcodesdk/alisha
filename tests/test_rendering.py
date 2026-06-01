from __future__ import annotations

import importlib.machinery
import importlib.util
import io
from pathlib import Path
import contextlib
import unittest

from rich.panel import Panel
from rich.text import Text


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
    def test_live_stream_is_used_only_for_tty_stdout(self) -> None:
        class FakeStdout:
            def __init__(self, value: bool) -> None:
                self.value = value

            def isatty(self) -> bool:
                return self.value

        self.assertTrue(alisha.should_use_live_stream(FakeStdout(True)))
        self.assertFalse(alisha.should_use_live_stream(FakeStdout(False)))
        self.assertFalse(alisha.should_use_live_stream(object()))

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

    def test_streaming_display_buffers_without_live_output_when_disabled(self) -> None:
        display = alisha.StreamingAnswerDisplay(enabled=False)

        display.start()
        display.append("hello")
        display.append(" world")
        display.finish_success()

        self.assertEqual(display.answer, "hello world")
        self.assertIsNone(display.live)

    def test_live_preview_is_plain_text_not_a_panel(self) -> None:
        preview = alisha.live_preview_text("streaming text", width=80, max_lines=4)

        self.assertIsInstance(preview, Text)
        self.assertNotIsInstance(preview, Panel)
        self.assertEqual(preview.plain, "streaming text")

    def test_live_preview_is_capped_to_recent_lines(self) -> None:
        preview = alisha.live_preview_text(
            "one\ntwo\nthree\nfour\nfive",
            width=80,
            max_lines=3,
        )

        self.assertEqual(preview.plain, "three\nfour\nfive")

    def test_live_preview_wraps_long_lines_before_capping(self) -> None:
        preview = alisha.live_preview_text("abcdefghij", width=4, max_lines=2)

        self.assertEqual(preview.plain, "efgh\nij")

    def test_blank_live_preview_matches_requested_height(self) -> None:
        preview = alisha.blank_live_preview(3)

        self.assertIsInstance(preview, Text)
        self.assertEqual(preview.plain, "\n\n")

    def test_partial_raw_answer_prints_clear_label(self) -> None:
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            alisha.print_partial_raw_answer("partial")

        self.assertEqual(output.getvalue(), "\n--- partial raw answer ---\npartial\n")


if __name__ == "__main__":
    unittest.main()
