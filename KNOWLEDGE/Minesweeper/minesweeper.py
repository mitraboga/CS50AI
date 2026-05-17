import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation.
    Handles board, mine placement, and neighbor counts.
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        self.mines = set()
        while len(self.mines) != mines:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation of the board (for debugging).
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            row = "|"
            for j in range(self.width):
                if self.board[i][j]:
                    row += "X|"
                else:
                    row += " |"
            print(row)
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines adjacent to a given cell.
        """
        (row, col) = cell
        count = 0
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):

                # Ignore the cell itself
                if (i, j) == (row, col):
                    continue

                # Check for valid cell indices
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game.

    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines:

        { (i1, j1), (i2, j2), ... } = count
    """

    def __init__(self, cells, count):
        # Cells: set of (i, j) tuples
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return isinstance(other, Sentence) and \
            self.cells == other.cells and \
            self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.

        Logic:
        - If number of cells == count (and not zero), all must be mines.
        """
        if len(self.cells) > 0 and len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.

        Logic:
        - If count == 0, none of them are mines → all safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates the sentence given that a cell is known to be a mine.

        If the cell is in this sentence:
        - Remove it from the set.
        - Decrease count by 1 (since that mine contributed to the count).
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates the sentence given that a cell is known to be safe.

        If the cell is in this sentence:
        - Remove it from the set.
        - Count stays the same.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player (AI).

    Knowledge-based agent that:
    - Stores logical sentences about the board.
    - Uses inference to find new safes and mines.
    - Uses a risk-based heuristic when guessing.
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Moves already made
        self.moves_made = set()

        # Cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # Knowledge base: list of Sentences known to be true
        self.knowledge = []

    # -----------------------------
    # Marking helpers
    # -----------------------------

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        if cell in self.mines:
            return False
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
        return True

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell in self.safes:
            return False
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        return True

    # -----------------------------
    # Core knowledge update
    # -----------------------------

    def add_knowledge(self, cell, count):
        """
        Called when the board tells us for a given safe cell
        how many neighboring cells have mines.

        This should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence about neighbors of this cell
        neighbours = set()
        x, y = cell

        # Loop through all potential neighbors (including diagonals)
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                neighbour = (i, j)

                # Skip the cell itself
                if neighbour == cell:
                    continue

                # Skip if known safe
                if neighbour in self.safes:
                    continue

                # If known mine, reduce count and skip adding
                if neighbour in self.mines:
                    count -= 1
                    continue

                # Only add valid board cells that are not already known safe/mine
                if (
                    0 <= i < self.height
                    and 0 <= j < self.width
                    and neighbour not in self.safes
                    and neighbour not in self.mines
                ):
                    neighbours.add(neighbour)

        if len(neighbours) > 0:
            self.knowledge.append(Sentence(neighbours, count))

        # 4 & 5) Repeatedly infer new safes/mines and new sentences
        self._update_knowledge()

    def _update_knowledge(self):
        """
        Internal method: repeatedly applies inference rules until
        no new information can be derived.

        Uses:
        - Sentence.known_safes / known_mines
        - Subset inference: if S1 ⊆ S2, then S2 - S1 has count2 - count1 mines.
        """

        changed = True
        while changed:
            changed = False

            # Collect new safes and mines from current sentences
            new_safes = set()
            new_mines = set()
            for sentence in self.knowledge:
                new_safes |= sentence.known_safes()
                new_mines |= sentence.known_mines()

            # Mark them globally
            for cell in new_safes - self.safes:
                if self.mark_safe(cell):
                    changed = True

            for cell in new_mines - self.mines:
                if self.mark_mine(cell):
                    changed = True

            # Remove empty and duplicate sentences
            cleaned = []
            seen = set()
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    continue
                key = (frozenset(sentence.cells), sentence.count)
                if key not in seen:
                    seen.add(key)
                    cleaned.append(sentence)
            if len(cleaned) != len(self.knowledge):
                changed = True
            self.knowledge = cleaned

            # Subset inference: S1 ⊂ S2 ⇒ S2 - S1 = c2 - c1
            new_sentences = []
            for s1, s2 in itertools.permutations(self.knowledge, 2):
                if not s1.cells or not s2.cells:
                    continue
                if s1.cells.issubset(s2.cells):
                    diff_cells = s2.cells - s1.cells
                    diff_count = s2.count - s1.count
                    if diff_count < 0 or len(diff_cells) == 0:
                        continue
                    candidate = Sentence(diff_cells, diff_count)
                    # Avoid duplicates
                    if candidate not in self.knowledge and candidate not in new_sentences:
                        new_sentences.append(candidate)

            if new_sentences:
                self.knowledge.extend(new_sentences)
                changed = True

    # -----------------------------
    # Move selection
    # -----------------------------

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the board.

        The move:
        - Must be known to be safe.
        - Must not already have been chosen.

        If no such move exists, returns None.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.

        Ultra-AI behavior:
        - Consider all cells that:
            1) have not been chosen
            2) are not known mines
        - Use a simple risk score from knowledge:
            risk(cell) = sum_over_sentences( count / |sentence_cells ∩ allowed| )
        - Choose the move(s) with the minimum risk, break ties randomly.
        """

        # All possible board cells
        all_cells = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
        ]

        # Allowed moves: not yet chosen, not known mines
        allowed = [
            cell for cell in all_cells
            if cell not in self.moves_made and cell not in self.mines
        ]

        if not allowed:
            return None

        # Initialize risk scores
        risk = {cell: 0.0 for cell in allowed}

        # For each sentence, distribute mine-count risk among the cells in that sentence
        for sentence in self.knowledge:
            if sentence.count <= 0 or len(sentence.cells) == 0:
                continue

            # Only consider cells from this sentence that are still candidate moves
            affected = [c for c in sentence.cells if c in allowed]
            if not affected:
                continue

            # Simple uniform risk distribution
            contribution = sentence.count / len(affected)
            for c in affected:
                risk[c] += contribution

        # Some cells might never appear in any sentence, they keep risk 0 → best
        min_risk = min(risk.values())
        best_cells = [c for c, r in risk.items() if r == min_risk]

        return random.choice(best_cells)
