import nltk
import sys
from nltk import CFG

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe"
N -> "she" | "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said"
V -> "sat" | "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP Conj VP

NP -> N
NP -> Det N
NP -> Det AdjP N
NP -> NP PP

AdjP -> Adj
AdjP -> Adj AdjP

VP -> V
VP -> V NP
VP -> V PP
VP -> V NP PP
VP -> Adv VP
VP -> VP Adv

PP -> P NP
"""

grammar = CFG.fromstring(TERMINALS + NONTERMINALS)
parser = nltk.ChartParser(grammar)


def preprocess(sentence):
    tokens = nltk.word_tokenize(sentence.lower())
    return [w for w in tokens if any(c.isalpha() for c in w)]


def np_chunk(tree):
    chunks = []
    for subtree in tree.subtrees(lambda t: t.label() == "NP"):
        if not any(
            child.label() == "NP"
            for child in subtree.subtrees(lambda t: t != subtree)
        ):
            chunks.append(subtree)
    return chunks


def main():

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            sentence = f.read()
    else:
        sentence = input("Sentence: ")

    words = preprocess(sentence)

    try:
        trees = list(parser.parse(words))
    except ValueError:
        print("Could not parse sentence.")
        return

    if not trees:
        print("Could not parse sentence.")
        return

    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


if __name__ == "__main__":
    main()
