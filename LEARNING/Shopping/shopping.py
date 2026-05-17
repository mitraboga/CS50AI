import csv
from sklearn.neighbors import KNeighborsClassifier


MONTHS = {
    "Jan": 0,
    "Feb": 1,
    "Mar": 2,
    "Apr": 3,
    "May": 4,
    "June": 5,
    "Jul": 6,
    "Aug": 7,
    "Sep": 8,
    "Oct": 9,
    "Nov": 10,
    "Dec": 11
}


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into
    a list of evidence lists and a list of labels.

    Returns:
        (evidence, labels)
            evidence: list of lists, each inner list has 17 values
            labels: list of integers, 1 for purchase, 0 otherwise
    """

    evidence = []
    labels = []

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Build evidence row in the specified order
            e = [
                int(row["Administrative"]),
                float(row["Administrative_Duration"]),
                int(row["Informational"]),
                float(row["Informational_Duration"]),
                int(row["ProductRelated"]),
                float(row["ProductRelated_Duration"]),
                float(row["BounceRates"]),
                float(row["ExitRates"]),
                float(row["PageValues"]),
                float(row["SpecialDay"]),
                MONTHS[row["Month"]],
                int(row["OperatingSystems"]),
                int(row["Browser"]),
                int(row["Region"]),
                int(row["TrafficType"]),
                # VisitorType: 1 for Returning_Visitor, 0 otherwise
                1 if row["VisitorType"] == "Returning_Visitor" else 0,
                # Weekend: 1 if TRUE, 0 otherwise
                1 if row["Weekend"] == "TRUE" else 0
            ]

            # Label: Revenue TRUE -> 1, FALSE -> 0
            label = 1 if row["Revenue"] == "TRUE" else 0

            evidence.append(e)
            labels.append(label)

    return evidence, labels


def train_model(evidence, labels):
    """
    Train and return a k-NN model (k = 1) using the provided training data.
    """

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)  # standard fit method for sklearn estimators
    return model


def evaluate(labels, predictions):
    """
    Given actual labels and predicted labels, return a tuple (sensitivity, specificity).

    sensitivity: proportion of actual positives correctly identified (TP / P)
    specificity: proportion of actual negatives correctly identified (TN / N)
    """

    # True positives, true negatives, false positives, false negatives
    tp = tn = fp = fn = 0

    for actual, predicted in zip(labels, predictions):
        if actual == 1:
            # Positive example
            if predicted == 1:
                tp += 1
            else:
                fn += 1
        else:
            # Negative example
            if predicted == 0:
                tn += 1
            else:
                fp += 1

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    return sensitivity, specificity
