import json
from sklearn import linear_model
import numpy as np


def read_labels(file_path):
    with open(file_path, "r") as file:
        labels = json.load(file)
    return labels


def main():
    all_labels = read_labels("image_processing/labels.json")
    true_labels: list[float] = all_labels["TRUE"]
    false_labels: list[float] = all_labels["FALSE"]
    print("TRUE count=", len(true_labels))
    print("FALSE count=", len(false_labels))

    # Prepare the data
    X = np.array(true_labels + false_labels)
    y = np.array([1] * len(true_labels) + [0] * len(false_labels))

    # Reshape the data
    X = X.reshape(-1, 512)

    # Train the linear regression model
    model = linear_model.LinearRegression()
    model.fit(X, y)

    # print("Model coefficients:", model.coef_)
    print("Model intercept:", model.intercept_)

    # Predict the labels
    predictions = model.predict(X)
    predicted_labels = [1 if pred >= 0.5 else 0 for pred in predictions]

    # Calculate the number of correct predictions
    correct_predictions = sum(1 for true, pred in zip(y, predicted_labels) if true == pred)
    print("Number of correct predictions:", correct_predictions)

    # UNSEEN IMAGES:
    true_test_labels: list[float] = all_labels["TRUE_TEST"]
    false_test_labels: list[float] = all_labels["FALSE_TEST"]

    print("TRUE_TEST count=", len(true_test_labels))
    print("FALSE_TEST count=", len(false_test_labels))

    # Prepare the data
    X = np.array(true_test_labels + false_test_labels)
    y = np.array([1] * len(true_test_labels) + [0] * len(false_test_labels))
    X = X.reshape(-1, 512)
    predictions = model.predict(X)
    predicted_labels = [1 if pred >= 0.5 else 0 for pred in predictions]

    correct_predictions = sum(1 for true, pred in zip(y, predicted_labels) if true == pred)

    print("UNSEEN IMAGES - number of correct predictions:", correct_predictions)


if __name__ == "__main__":
    main()
