import csv
import sys

from util import Node, QueueFrontier

# Global data stores (must remain exactly these names for check50)
names = {}
people = {}
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.

    Expects directory to contain:
      - people.csv with id, name, birth
      - movies.csv with id, title, year
      - stars.csv with person_id, movie_id

    Populates:
      - people[id] = {"name": str, "birth": str, "movies": set()}
      - movies[id] = {"title": str, "year": str, "stars": set()}
      - names[lower_name] = set([id, ...])  (handles duplicate names)
    """
    print("Loading data...")

    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            key = row["name"].lower()
            if key in names:
                names[key].add(row["id"])
            else:
                names[key] = {row["id"]}

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars (edges)
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["person_id"]
            movie_id = row["movie_id"]
            # Only add edges that reference known ids
            if person_id in people and movie_id in movies:
                people[person_id]["movies"].add(movie_id)
                movies[movie_id]["stars"].add(person_id)

    print("Data loaded.")


def main():
    # Which directory to load from (default "large" if not specified)
    if len(sys.argv) == 2:
        directory = sys.argv[1]
    else:
        directory = "large"

    load_data(directory)

    source_name = input("Name: ")
    source = person_id_for_name(source_name)
    if source is None:
        print("Person not found.")
        sys.exit(0)

    target_name = input("Name: ")
    target = person_id_for_name(target_name)
    if target is None:
        print("Person not found.")
        sys.exit(0)

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
        return

    degrees = len(path)
    print(f"{degrees} degrees of separation.")

    # Print path
    current = source
    for i, (movie_id, person_id) in enumerate(path, start=1):
        movie = movies[movie_id]["title"]
        actor1 = people[current]["name"]
        actor2 = people[person_id]["name"]
        print(f"{i}: {actor1} and {actor2} starred in {movie}")
        current = person_id


def person_id_for_name(name):
    """
    Resolve a person's ID given their name.
    If multiple people have the same name, prompt for the intended ID.
    Returns None if the person does not exist.
    """
    person_ids = names.get(name.lower(), set())
    if len(person_ids) == 0:
        return None
    elif len(person_ids) == 1:
        return next(iter(person_ids))
    else:
        print(f"Which '{name}'?")
        for pid in person_ids:
            person = people[pid]
            print(f"ID: {pid}, Name: {person['name']}, Birth: {person['birth']}")
        try:
            pid = input("Intended Person ID: ")
        except EOFError:
            return None
        if pid in person_ids:
            return pid
        return None


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people who starred with a given person.
    """
    neighbor_pairs = set()
    for m in people[person_id]["movies"]:
        for p in movies[m]["stars"]:
            neighbor_pairs.add((m, p))
    return neighbor_pairs


def shortest_path(source, target):
    """
    Return the shortest list of (movie_id, person_id) pairs that connect
    the actor with id `source` to the actor with id `target` using BFS.
    If no connection exists, return None.
    """

    # Trivial case: same person => zero degrees
    if source == target:
        return []

    # Frontier holds Node(state=person_id, parent=Node, action=movie_id)
    frontier = QueueFrontier()
    start = Node(state=source, parent=None, action=None)
    frontier.add(start)

    explored = set()
    # Track states currently in frontier to avoid linear scans
    frontier_states = {source}

    def reconstruct_path(goal_node):
        steps = []
        node = goal_node
        while node.parent is not None:
            steps.append((node.action, node.state))  # (movie_id, person_id)
            node = node.parent
        steps.reverse()
        return steps

    # Standard BFS
    while not frontier.empty():
        node = frontier.remove()
        frontier_states.discard(node.state)
        explored.add(node.state)

        for movie_id, person_id in neighbors_for_person(node.state):
            if person_id in explored or person_id in frontier_states:
                continue

            child = Node(state=person_id, parent=node, action=movie_id)

            # Early goal check: return as soon as we generate the target
            if person_id == target:
                return reconstruct_path(child)

            frontier.add(child)
            frontier_states.add(person_id)

    # No path found
    return None


if __name__ == "__main__":
    main()
