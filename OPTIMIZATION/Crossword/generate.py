import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        self.crossword = crossword
        self.domains = {
            var: set(crossword.words)
            for var in crossword.variables
        }

    def letter_grid(self, assignment):
        grid = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]

        for variable, word in assignment.items():
            for k in range(variable.length):
                i = variable.i + (k if variable.direction == Variable.DOWN else 0)
                j = variable.j + (k if variable.direction == Variable.ACROSS else 0)
                grid[i][j] = word[k]
        return grid

    def print(self, assignment):
        grid = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(grid[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border

        letters = self.letter_grid(assignment)

        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("arial.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]

                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (j * cell_size + (interior_size - w) / 2,
                             i * cell_size + (interior_size - h) / 2),
                            letters[i][j], fill="black", font=font
                        )
                else:
                    draw.rectangle(rect, fill="black")

        img.save(filename)

    # -------------------- CSP METHODS --------------------

    def solve(self):
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        for var in self.domains:
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        i, j = overlap

        for word_x in set(self.domains[x]):
            if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        if arcs is None:
            queue = [(x, y) for x in self.domains for y in self.crossword.neighbors(x)]
        else:
            queue = arcs.copy()

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        return set(assignment.keys()) == self.crossword.variables

    def consistent(self, assignment):
        words = set()

        for var, word in assignment.items():
            if len(word) != var.length:
                return False
            if word in words:
                return False
            words.add(word)

            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap:
                        i, j = overlap
                        if word[i] != assignment[neighbor][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        counts = {}

        for value in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap:
                    i, j = overlap
                    for neighbor_value in self.domains[neighbor]:
                        if value[i] != neighbor_value[j]:
                            count += 1
            counts[value] = count

        return sorted(self.domains[var], key=lambda v: counts[v])

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        return min(
            unassigned,
            key=lambda v: (len(self.domains[v]), -len(self.crossword.neighbors(v)))
        )

    def backtrack(self, assignment):
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                domains_backup = copy.deepcopy(self.domains)
                self.domains[var] = {value}

                if self.ac3([(n, var) for n in self.crossword.neighbors(var)]):
                    result = self.backtrack(new_assignment)
                    if result:
                        return result

                self.domains = domains_backup

        return None


def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
