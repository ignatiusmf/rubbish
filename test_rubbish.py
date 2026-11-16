import contextlib
import io
import os
import random
import re
import subprocess
import sys
import unittest
from pathlib import Path

import rubbish

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "rubbish.py"
WORD = re.compile(r"^[a-z]+$")
SENTENCE = re.compile(
    r"^The ([a-z]+) ([a-z]+) ([a-z]+) ([a-z]+) (an?) ([a-z]+) ([a-z]+)\.$"
)
VOWELS = "aeiou"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=30,
    )


class WordTupleTests(unittest.TestCase):
    TUPLES = ("ADJECTIVES", "NOUNS", "VERBS", "ADVERBS")

    def test_tuples_of_distinct_lowercase_words(self):
        for name in self.TUPLES:
            with self.subTest(name=name):
                words = getattr(rubbish, name)
                self.assertIsInstance(words, tuple)
                self.assertGreaterEqual(len(words), 12)
                self.assertEqual(len(words), len(set(words)))
                for word in words:
                    self.assertIsInstance(word, str)
                    self.assertRegex(word, WORD)

    def test_adverbs_end_in_ly(self):
        for word in rubbish.ADVERBS:
            self.assertTrue(word.endswith("ly"), word)

    def test_adjectives_start_with_both_kinds_of_letter(self):
        vowel = [w for w in rubbish.ADJECTIVES if w[0] in VOWELS]
        self.assertGreaterEqual(len(vowel), 3)
        self.assertGreaterEqual(len(rubbish.ADJECTIVES) - len(vowel), 3)


class TalkTests(unittest.TestCase):
    def test_form_slots_and_article(self):
        rng = random.Random(12345)
        articles = set()
        for _ in range(600):
            sentence = rubbish.talk(rng)
            self.assertIsInstance(sentence, str)
            self.assertEqual(sentence, sentence.strip())
            match = SENTENCE.match(sentence)
            self.assertIsNotNone(match, sentence)
            adj1, noun1, adverb, verb, article, adj2, noun2 = match.groups()
            self.assertIn(adj1, rubbish.ADJECTIVES)
            self.assertIn(noun1, rubbish.NOUNS)
            self.assertIn(adverb, rubbish.ADVERBS)
            self.assertIn(verb, rubbish.VERBS)
            self.assertIn(adj2, rubbish.ADJECTIVES)
            self.assertIn(noun2, rubbish.NOUNS)
            self.assertEqual(article, "an" if adj2[0] in VOWELS else "a", sentence)
            articles.add(article)
        self.assertEqual(articles, {"a", "an"})

    def test_ignores_global_random_state(self):
        first_rng, second_rng = random.Random(7), random.Random(7)
        random.seed(1)
        first = [rubbish.talk(first_rng) for _ in range(20)]
        random.seed(99999)
        second = [rubbish.talk(second_rng) for _ in range(20)]
        self.assertEqual(first, second)


class MainTests(unittest.TestCase):
    def test_returns_zero_and_prints_count_lines(self):
        for argv, count in ((["--seed", "3"], 1), (["-n", "5", "-s", "3"], 5)):
            with self.subTest(argv=argv):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    status = rubbish.main(argv)
                self.assertEqual(status, 0)
                self.assertTrue(out.getvalue().endswith("\n"))
                lines = out.getvalue().splitlines()
                self.assertEqual(len(lines), count)
                for line in lines:
                    self.assertRegex(line, SENTENCE)


class CommandLineTests(unittest.TestCase):
    def test_single_line_by_default(self):
        result = run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertRegex(lines[0], SENTENCE)

    def test_count_options(self):
        for args in (("-n", "4"), ("--count", "4")):
            with self.subTest(args=args):
                result = run_cli(*args)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stderr, "")
                self.assertEqual(len(result.stdout.splitlines()), 4)

    def test_same_seed_same_output(self):
        first = run_cli("--seed", "42", "-n", "6")
        second = run_cli("-s", "42", "--count", "6")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stderr, "")
        self.assertEqual(len(first.stdout.splitlines()), 6)
        self.assertEqual(first.stdout, second.stdout)

    def test_prefix_property(self):
        short = run_cli("-s", "11", "-n", "3").stdout.splitlines()
        full = run_cli("-s", "11", "-n", "9").stdout.splitlines()
        self.assertEqual(len(short), 3)
        self.assertEqual(len(full), 9)
        self.assertEqual(short, full[:3])

    def test_output_matches_talk_on_one_generator(self):
        rng = random.Random(2024)
        expected = [rubbish.talk(rng) for _ in range(8)]
        result = run_cli("--seed", "2024", "-n", "8")
        self.assertEqual(result.stdout.splitlines(), expected)

    def test_seeds_differ(self):
        outputs = {run_cli("-s", str(seed), "-n", "3").stdout for seed in range(20)}
        self.assertGreater(len(outputs), 1)

    def test_usage_errors(self):
        bad = [("-n", value) for value in ("0", "-3", "abc", "1.5")]
        bad += [("--count=-3",), ("-s", "abc"), ("--seed", "1.5")]
        for args in bad:
            with self.subTest(args=args):
                result = run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotEqual(result.stderr.strip(), "")

    def test_shebang_and_executable_bit(self):
        with SCRIPT.open(encoding="utf-8") as handle:
            self.assertEqual(handle.readline().rstrip("\n"), "#!/usr/bin/env python3")
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_import_prints_nothing(self):
        result = subprocess.run(
            [sys.executable, "-c", "import rubbish"],
            capture_output=True, text=True, timeout=30, cwd=HERE,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
