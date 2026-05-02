"""Tests for T1/T3/T4/T5 table generators in generate_paper_figures.py."""
from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestT1OverallPass:
    def test_generates_valid_latex_with_correct_counts(self, tmp_path):
        from scripts.generate_paper_figures import generate_t1_overall_pass

        generate_t1_overall_pass(PROJECT_ROOT, tmp_path, verbose=True)

        out = tmp_path / "t1_overall_pass.tex"
        assert out.exists(), "t1_overall_pass.tex not created"

        content = out.read_text()
        assert r"\begin{tabular}" in content
        assert r"\end{tabular}" in content
        # Known PASS counts from quantitative_findings JSONs
        assert "230" in content  # Qwen PASS count
        assert "621" in content  # GPT-5.4 PASS count
        assert "604" in content  # Codex PASS count
        # Known totals
        assert "626" in content  # Qwen total
        assert "822" in content  # GPT-5.4 total
        assert "814" in content  # Codex total


class TestT3Passk:
    def test_generates_valid_latex_with_correct_passk(self, tmp_path):
        from scripts.generate_paper_figures import generate_t3_passk

        generate_t3_passk(PROJECT_ROOT, tmp_path, verbose=True)

        out = tmp_path / "t3_passk.tex"
        assert out.exists(), "t3_passk.tex not created"

        content = out.read_text()
        assert r"\begin{tabular}" in content
        assert r"\end{tabular}" in content
        assert "142" in content  # n_tasks per model
        assert "23.9" in content  # Qwen pass@1
        assert "62.7" in content  # GPT-5.4 pass@1
        assert "35.2" in content  # Qwen pass@3
        assert "69.7" in content  # GPT-5.4 pass@3


class TestT4Augmentation:
    def test_generates_valid_latex_with_augmentation_rates(self, tmp_path):
        from scripts.generate_paper_figures import generate_t4_augmentation

        generate_t4_augmentation(PROJECT_ROOT, tmp_path, verbose=True)

        out = tmp_path / "t4_augmentation.tex"
        assert out.exists(), "t4_augmentation.tex not created"

        content = out.read_text()
        assert r"\begin{tabular}" in content
        assert r"\end{tabular}" in content
        assert "62.7" in content  # Codex/GPT-5.4 L0 rate
        assert "23.9" in content  # Qwen L0 rate
        assert "L0" in content
        assert "L4" in content


class TestT5Stats:
    def test_generates_valid_latex_with_pairwise_tests(self, tmp_path):
        from scripts.generate_paper_figures import generate_t5_stats

        generate_t5_stats(PROJECT_ROOT, tmp_path, verbose=True)

        out = tmp_path / "t5_stats.tex"
        assert out.exists(), "t5_stats.tex not created"

        content = out.read_text()
        assert r"\begin{tabular}" in content
        assert r"\end{tabular}" in content
        assert "Codex" in content or "codex" in content
        assert "Qwen" in content or "qwen" in content
        assert "0.931" in content  # Codex vs GPT-5.4 OR
        assert "4.952" in content  # Codex vs Qwen OR
