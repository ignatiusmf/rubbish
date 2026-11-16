#!/usr/bin/env python3
"""Talk rubbish: print procedurally generated nonsense sentences."""

import argparse
import random
import sys

ADJECTIVES = (
    "invisible", "enormous", "orange", "oblong", "elastic", "airtight",
    "imaginary", "ornamental", "soggy", "wobbly", "dusty", "lopsided",
    "squeaky", "lukewarm", "purple", "tiny", "rusty", "fluffy",
)

NOUNS = (
    "teapot", "ladder", "stapler", "otter", "umbrella", "biscuit",
    "lantern", "kettle", "sofa", "bucket", "pigeon", "trombone",
    "cushion", "turnip", "hedgehog", "envelope", "wheelbarrow", "pancake",
)

VERBS = (
    "juggles", "polishes", "catalogues", "admires", "borrows", "waters",
    "measures", "paints", "labels", "wraps", "inspects", "rearranges",
    "balances", "photographs", "sketches", "dusts",
)

ADVERBS = (
    "solemnly", "briskly", "carefully", "cheerfully", "quietly", "proudly",
    "slowly", "gently", "politely", "patiently", "loudly", "neatly",
    "calmly", "reluctantly",
)


def talk(rng):
    """Return one nonsense sentence, drawing randomness only from rng."""
    subject = f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}"
    action = f"{rng.choice(ADVERBS)} {rng.choice(VERBS)}"
    adjective = rng.choice(ADJECTIVES)
    article = "an" if adjective[0] in "aeiou" else "a"
    return f"The {subject} {action} {article} {adjective} {rng.choice(NOUNS)}."


def _count(text):
    try:
        value = int(text)
    except ValueError:
        value = 0
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be an integer of at least 1: {text!r}")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rubbish", description=__doc__)
    parser.add_argument("-n", "--count", type=_count, default=1, metavar="N",
                        help="how many sentences to print (default: 1)")
    parser.add_argument("-s", "--seed", type=int, default=None, metavar="SEED",
                        help="integer seed for reproducible output")
    args = parser.parse_args(argv)
    rng = random.Random() if args.seed is None else random.Random(args.seed)
    for _ in range(args.count):
        print(talk(rng))
    return 0


if __name__ == "__main__":
    sys.exit(main())
