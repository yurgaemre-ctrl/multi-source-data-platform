from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


OUTPUT_DIR = Path("data/model_output")
FIGURE_DIR = Path("data/model_output/figures")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


predictions = pd.read_csv(
    OUTPUT_DIR / "predictions.csv",
    parse_dates=["date"],
)

metrics = pd.read_csv(
    OUTPUT_DIR / "model_metrics.csv"
)


# 1. Actual versus predicted returns over time
plt.figure(figsize=(12, 6))

plt.plot(
    predictions["date"],
    predictions["actual_return"],
    label="Actual SPY return",
)

plt.plot(
    predictions["date"],
    predictions["ridge_prediction"],
    label="Ridge prediction",
)

plt.plot(
    predictions["date"],
    predictions["neural_prediction"],
    label="Neural-network prediction",
)

plt.axhline(0, linewidth=0.8)

plt.title("Out-of-Sample Monthly SPY Returns: Actual vs Predicted")
plt.xlabel("Date")
plt.ylabel("Monthly return")
plt.legend()
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "actual_vs_predicted.png",
    dpi=200,
)

plt.close()


# 2. Model error comparison
error_metrics = metrics.set_index("model")[["RMSE", "MAE"]]

ax = error_metrics.plot(
    kind="bar",
    figsize=(8, 5),
)

ax.set_title("Out-of-Sample Prediction Error")
ax.set_xlabel("")
ax.set_ylabel("Error")
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "model_error_comparison.png",
    dpi=200,
)

plt.close()


# 3. Actual versus predicted scatter plots
fig, axes = plt.subplots(
    1,
    2,
    figsize=(11, 5),
    sharex=True,
    sharey=True,
)

axes[0].scatter(
    predictions["actual_return"],
    predictions["ridge_prediction"],
)

axes[0].set_title("Ridge Regression")
axes[0].set_xlabel("Actual return")
axes[0].set_ylabel("Predicted return")

axes[1].scatter(
    predictions["actual_return"],
    predictions["neural_prediction"],
)

axes[1].set_title("Neural Network")
axes[1].set_xlabel("Actual return")

minimum = min(
    predictions[
        [
            "actual_return",
            "ridge_prediction",
            "neural_prediction",
        ]
    ].min()
)

maximum = max(
    predictions[
        [
            "actual_return",
            "ridge_prediction",
            "neural_prediction",
        ]
    ].max()
)

for ax in axes:
    ax.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--",
    )

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "actual_vs_predicted_scatter.png",
    dpi=200,
)

plt.close()


print("Created:")
print(FIGURE_DIR / "actual_vs_predicted.png")
print(FIGURE_DIR / "model_error_comparison.png")
print(FIGURE_DIR / "actual_vs_predicted_scatter.png")