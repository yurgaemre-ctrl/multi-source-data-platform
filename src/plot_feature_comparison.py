import os

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = "data/model_output/model_metrics_feature_comparison.csv"
OUTPUT_DIR = "docs/images"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = pd.read_csv(INPUT_FILE)

    specification_order = [
        "Levels",
        "Changes/Growth",
        "Combined",
    ]

    model_order = [
        "Ridge regression",
        "Neural network",
    ]

    results["specification"] = pd.Categorical(
        results["specification"],
        categories=specification_order,
        ordered=True,
    )

    results["model"] = pd.Categorical(
        results["model"],
        categories=model_order,
        ordered=True,
    )

    results = results.sort_values(
        ["specification", "model"]
    )

    # ---------------------------------------------------------
    # Figure 1: RMSE comparison
    # ---------------------------------------------------------
    rmse_table = results.pivot(
        index="specification",
        columns="model",
        values="RMSE",
    ).reindex(specification_order)

    ax = rmse_table.plot(
        kind="bar",
        figsize=(9, 6),
    )

    ax.set_title(
        "Out-of-Sample Prediction Error by Macro Feature Representation"
    )
    ax.set_xlabel("Macro feature representation")
    ax.set_ylabel("RMSE")
    ax.tick_params(
        axis="x",
        rotation=0,
    )

    ax.legend(
        title="Model"
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.4f",
            padding=3,
        )

    plt.tight_layout()

    rmse_path = os.path.join(
        OUTPUT_DIR,
        "feature_representation_rmse.png",
    )

    plt.savefig(
        rmse_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # ---------------------------------------------------------
    # Figure 2: Out-of-sample R² comparison
    # ---------------------------------------------------------
    r2_table = results.pivot(
        index="specification",
        columns="model",
        values="R2",
    ).reindex(specification_order)

    ax = r2_table.plot(
        kind="bar",
        figsize=(9, 6),
    )

    ax.set_title(
        "Out-of-Sample R² by Macro Feature Representation"
    )
    ax.set_xlabel("Macro feature representation")
    ax.set_ylabel("Out-of-sample R²")
    ax.tick_params(
        axis="x",
        rotation=0,
    )

    ax.axhline(
        y=0,
        linewidth=1,
    )

    ax.legend(
        title="Model"
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.3f",
            padding=3,
        )

    plt.tight_layout()

    r2_path = os.path.join(
        OUTPUT_DIR,
        "feature_representation_r2.png",
    )

    plt.savefig(
        r2_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # ---------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------
    print("\nFeature representation comparison:")
    print(
        results[
            [
                "specification",
                "model",
                "RMSE",
                "MAE",
                "R2",
            ]
        ].to_string(index=False)
    )

    print("\nFigures saved to:")
    print(rmse_path)
    print(r2_path)


if __name__ == "__main__":
    main()