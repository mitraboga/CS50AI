import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    people = load_data(sys.argv[1])

    probabilities = {
        person: {
            "gene": {0: 0, 1: 0, 2: 0},
            "trait": {True: 0, False: 0}
        }
        for person in people
    }

    names = set(people)

    for have_trait in powerset(names):

        fails_evidence = any(
            (people[p]["trait"] is not None and
             people[p]["trait"] != (p in have_trait))
            for p in names
        )

        if fails_evidence:
            continue

        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    normalize(probabilities)

    for person in people:
        print(f"{person}:")
        for category in probabilities[person]:
            print(f"  {category.capitalize()}:")
            for value in probabilities[person][category]:
                print(f"    {value}: {probabilities[person][category][value]:.4f}")


def load_data(filename):
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": True if row["trait"] == "1"
                else False if row["trait"] == "0"
                else None
            }
    return data


def powerset(s):
    s = list(s)
    return [
        set(combo) for combo in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    global PROBS

    probability = 1

    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]

        if person in two_genes:
            genes = 2
        elif person in one_gene:
            genes = 1
        else:
            genes = 0

        has_trait = person in have_trait
        trait_prob = PROBS["trait"][genes][has_trait]

        if mother is None and father is None:
            gene_prob = PROBS["gene"][genes]
        else:

            def inherit(parent):
                if parent in two_genes:
                    return 1 - PROBS["mutation"]
                elif parent in one_gene:
                    return 0.5
                else:
                    return PROBS["mutation"]

            mom = inherit(mother)
            dad = inherit(father)

            if genes == 2:
                gene_prob = mom * dad
            elif genes == 1:
                gene_prob = mom * (1 - dad) + (1 - mom) * dad
            else:
                gene_prob = (1 - mom) * (1 - dad)

        probability *= gene_prob * trait_prob

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):

    for person in probabilities:

        if person in two_genes:
            genes = 2
        elif person in one_gene:
            genes = 1
        else:
            genes = 0

        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):

    for person in probabilities:
        for category in probabilities[person]:
            total = sum(probabilities[person][category].values())
            for key in probabilities[person][category]:
                probabilities[person][category][key] /= total


if __name__ == "__main__":
    main()
