from logic import *

# Base symbols: roles of A, B, C
AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Extra symbols for Puzzle 3: what A actually said
AsaidKnight = Symbol("A said 'I am a Knight'")
AsaidKnave = Symbol("A said 'I am a Knave'")


def character(K, N):
    """
    Each character is exactly one of: Knight or Knave.
    """
    return And(
        Or(K, N),          # At least one
        Not(And(K, N))     # Not both
    )


# =====================================================================
# PUZZLE 0
# A says: "I am both a knight and a knave."
# =====================================================================

A_statement_0 = And(AKnight, AKnave)

knowledge0 = And(
    character(AKnight, AKnave),

    # If A is a knight, the statement must be true
    Implication(AKnight, A_statement_0),

    # If A is a knave, the statement must be false
    Implication(AKnave, Not(A_statement_0))
)


# =====================================================================
# PUZZLE 1
# A says: "We are both knaves."
# B says nothing.
# =====================================================================

A_statement_1 = And(AKnave, BKnave)

knowledge1 = And(
    character(AKnight, AKnave),
    character(BKnight, BKnave),

    Implication(AKnight, A_statement_1),
    Implication(AKnave, Not(A_statement_1))
)


# =====================================================================
# PUZZLE 2
# A says: "We are the same kind."
# B says: "We are of different kinds."
# =====================================================================

# A: "We are the same kind."
A_statement_2 = Or(
    And(AKnight, BKnight),
    And(AKnave, BKnave)
)

# B: "We are of different kinds."
B_statement_2 = Or(
    And(AKnight, BKnave),
    And(AKnave, BKnight)
)

knowledge2 = And(
    character(AKnight, AKnave),
    character(BKnight, BKnave),

    Implication(AKnight, A_statement_2),
    Implication(AKnave, Not(A_statement_2)),

    Implication(BKnight, B_statement_2),
    Implication(BKnave, Not(B_statement_2))
)


# =====================================================================
# PUZZLE 3
#
# A says either "I am a knight." OR "I am a knave." (but we don't know which)
# B says: "A said 'I am a knave'."
# B also says: "C is a knave."
# C says: "A is a knight."
# =====================================================================

# Content of the possible things A might say
A_sentence_knight = AKnight   # "I am a knight."
A_sentence_knave = AKnave     # "I am a knave."

# B's statements:
B_statement_1 = AsaidKnave    # "A said 'I am a knave'."
B_statement_2 = CKnave        # "C is a knave."

# C's statement:
C_statement = AKnight         # "A is a knight."

knowledge3 = And(
    character(AKnight, AKnave),
    character(BKnight, BKnave),
    character(CKnight, CKnave),

    # A said exactly one of the two sentences
    Or(AsaidKnight, AsaidKnave),
    Not(And(AsaidKnight, AsaidKnave)),

    # If A is a knight, then what he said must be TRUE.
    #   - If he said "I am a knight"  → AKnight is true
    #   - If he said "I am a knave"   → AKnave is true
    Implication(
        AKnight,
        Or(
            And(AsaidKnight, A_sentence_knight),
            And(AsaidKnave, A_sentence_knave)
        )
    ),

    # If A is a knave, then what he said must be FALSE.
    #   - If he said "I am a knight"  → AKnight is false
    #   - If he said "I am a knave"   → AKnave is false
    Implication(
        AKnave,
        Or(
            And(AsaidKnight, Not(A_sentence_knight)),
            And(AsaidKnave, Not(A_sentence_knave))
        )
    ),

    # B's first statement: "A said 'I am a knave'."
    Implication(BKnight, B_statement_1),
    Implication(BKnave, Not(B_statement_1)),

    # B's second statement: "C is a knave."
    Implication(BKnight, B_statement_2),
    Implication(BKnave, Not(B_statement_2)),

    # C's statement: "A is a knight."
    Implication(CKnight, C_statement),
    Implication(CKnave, Not(C_statement))
)


# =====================================================================
# Model checking driver
# =====================================================================

def main():
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]

    symbols = [
        AKnight, AKnave,
        BKnight, BKnave,
        CKnight, CKnave
    ]

    for name, kb in puzzles:
        print(name)
        for s in symbols:
            if model_check(kb, s):
                print(f"    {s}")


if __name__ == "__main__":
    main()
