import os
from dotenv import load_dotenv

load_dotenv()

import numpy as np
import pandas as pd
import psycopg
import torch
import torch.nn as nn

from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "platform"),
        user=os.getenv("POSTGRES_USER", "platform_user"),
        password=os.environ["POSTGRES_PASSWORD"],
    )


def load_market_data(connection):
    query = """
    SELECT
        d.full_date,
        a.symbol,
        f.source,
        f.adjusted_close
    FROM curated.fact_market f
    JOIN curated.dim_date d
        ON f.date_key = d.date_key
    JOIN curated.dim_asset a
        ON f.asset_key = a.asset_key
    WHERE a.symbol IN ('SPY', '^VIX')
      AND f.source = 'yahoo'
    ORDER BY d.full_date;
    """
    return pd.read_sql(query, connection)


def load_macro_data(connection):
    query = """
    SELECT
        d.full_date,
        s.series_id,
        f.value
    FROM curated.fact_macro f
    JOIN curated.dim_date d
        ON f.date_key = d.date_key
    JOIN curated.dim_macro_series s
        ON f.macro_series_key = s.macro_series_key
    ORDER BY d.full_date;
    """
    return pd.read_sql(query, connection)


def build_monthly_dataset(market, macro):
    market["full_date"] = pd.to_datetime(market["full_date"])
    macro["full_date"] = pd.to_datetime(macro["full_date"])

    prices = (
        market.pivot_table(
            index="full_date",
            columns="symbol",
            values="adjusted_close",
            aggfunc="last",
        )
        .sort_index()
    )

    monthly_market = pd.DataFrame(index=prices.resample("ME").last().index)

    spy_monthly = prices["SPY"].resample("ME").last()
    vix_monthly = prices["^VIX"].resample("ME").last()

    daily_spy_returns = prices["SPY"].pct_change()

    monthly_market["spy_return"] = spy_monthly.pct_change()
    monthly_market["spy_volatility"] = (
        daily_spy_returns.resample("ME").std() * np.sqrt(21)
    )
    monthly_market["vix"] = vix_monthly

    macro_wide = (
        macro.pivot_table(
            index="full_date",
            columns="series_id",
            values="value",
            aggfunc="last",
        )
        .sort_index()
        .resample("ME")
        .last()
        .ffill()
    )

    macro_wide = macro_wide[
        [
            "FEDFUNDS",
            "CPIAUCSL",
            "UNRATE",
            "GS10",
            "INDPRO",
            "PAYEMS",
            "M2SL",
        ]
    ]

    # ---------------------------------------------------------
    # 1. Macro levels
    # ---------------------------------------------------------
    macro_levels = macro_wide.copy()

    # ---------------------------------------------------------
    # 2. Macro changes / growth rates
    #
    # Interest rates and unemployment:
    #   first differences in percentage points
    #
    # CPI, industrial production, payrolls and M2:
    #   log growth rates
    # ---------------------------------------------------------
    macro_changes = pd.DataFrame(index=macro_wide.index)

    macro_changes["FEDFUNDS"] = macro_wide["FEDFUNDS"].diff()
    macro_changes["UNRATE"] = macro_wide["UNRATE"].diff()
    macro_changes["GS10"] = macro_wide["GS10"].diff()

    macro_changes["CPIAUCSL"] = np.log(macro_wide["CPIAUCSL"]).diff()
    macro_changes["INDPRO"] = np.log(macro_wide["INDPRO"]).diff()
    macro_changes["PAYEMS"] = np.log(macro_wide["PAYEMS"]).diff()
    macro_changes["M2SL"] = np.log(macro_wide["M2SL"]).diff()

    # ---------------------------------------------------------
    # 3. Lag both representations by one month
    # ---------------------------------------------------------
    macro_levels_lagged = macro_levels.shift(1).add_prefix("lag_level_")
    macro_changes_lagged = macro_changes.shift(1).add_prefix("lag_change_")

    macro_features = pd.concat(
        [
            macro_levels_lagged,
            macro_changes_lagged,
        ],
        axis=1,
    )

    data = monthly_market.join(
        macro_features,
        how="inner",
    )

    data["target_next_month_return"] = data["spy_return"].shift(-1)

    return data.dropna()


class MarketMLP(nn.Module):
    def __init__(self, input_size):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, x):
        return self.network(x)


def regression_metrics(y_true, y_pred):
    return {
        "RMSE": np.sqrt(
            mean_squared_error(
                y_true,
                y_pred,
            )
        ),
        "MAE": mean_absolute_error(
            y_true,
            y_pred,
        ),
        "R2": r2_score(
            y_true,
            y_pred,
        ),
    }


def main():
    np.random.seed(42)
    torch.manual_seed(42)

    with get_connection() as connection:
        market = load_market_data(connection)
        macro = load_macro_data(connection)

    data = build_monthly_dataset(
        market,
        macro,
    )

    # ---------------------------------------------------------
    # Market features are identical in every specification
    # ---------------------------------------------------------
    market_features = [
        "spy_return",
        "spy_volatility",
        "vix",
    ]

    # ---------------------------------------------------------
    # Macro levels
    # ---------------------------------------------------------
    level_features = [
        "lag_level_FEDFUNDS",
        "lag_level_CPIAUCSL",
        "lag_level_UNRATE",
        "lag_level_GS10",
        "lag_level_INDPRO",
        "lag_level_PAYEMS",
        "lag_level_M2SL",
    ]

    # ---------------------------------------------------------
    # Macro changes / growth
    # ---------------------------------------------------------
    change_features = [
        "lag_change_FEDFUNDS",
        "lag_change_CPIAUCSL",
        "lag_change_UNRATE",
        "lag_change_GS10",
        "lag_change_INDPRO",
        "lag_change_PAYEMS",
        "lag_change_M2SL",
    ]

    # ---------------------------------------------------------
    # Three specifications
    # ---------------------------------------------------------
    specifications = {
        "Levels": (
            market_features
            + level_features
        ),
        "Changes/Growth": (
            market_features
            + change_features
        ),
        "Combined": (
            market_features
            + level_features
            + change_features
        ),
    }

    y = data["target_next_month_return"]

    # Same chronological split for all specifications
    split_index = int(len(data) * 0.80)

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    all_results = []

    predictions_output = pd.DataFrame(
        {
            "date": data.index[split_index:],
            "actual_return": y_test.values,
        }
    )

    # ---------------------------------------------------------
    # Run each feature specification
    # ---------------------------------------------------------
    for specification_name, feature_columns in specifications.items():

        print(
            f"\nRunning specification: "
            f"{specification_name}"
        )

        X = data[feature_columns]

        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]

        scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(
            X_train
        )

        X_test_scaled = scaler.transform(
            X_test
        )

        # =====================================================
        # Ridge regression
        # =====================================================
        baseline = Ridge(
            alpha=1.0
        )

        baseline.fit(
            X_train_scaled,
            y_train,
        )

        baseline_predictions = baseline.predict(
            X_test_scaled
        )

        baseline_metrics = regression_metrics(
            y_test,
            baseline_predictions,
        )

        all_results.append(
            {
                "specification": specification_name,
                "model": "Ridge regression",
                **baseline_metrics,
            }
        )

        # =====================================================
        # Neural network
        # =====================================================
        # Reset seed so every specification begins from a
        # reproducible initialization.
        torch.manual_seed(42)

        X_train_tensor = torch.tensor(
            X_train_scaled,
            dtype=torch.float32,
        )

        y_train_tensor = torch.tensor(
            y_train.values.reshape(-1, 1),
            dtype=torch.float32,
        )

        X_test_tensor = torch.tensor(
            X_test_scaled,
            dtype=torch.float32,
        )

        model = MarketMLP(
            X_train_scaled.shape[1]
        )

        loss_function = nn.MSELoss()

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=0.001,
            weight_decay=0.0001,
        )

        model.train()

        for epoch in range(500):

            optimizer.zero_grad()

            predictions = model(
                X_train_tensor
            )

            loss = loss_function(
                predictions,
                y_train_tensor,
            )

            loss.backward()

            optimizer.step()

        model.eval()

        with torch.no_grad():

            neural_predictions = (
                model(
                    X_test_tensor
                )
                .numpy()
                .flatten()
            )

        neural_metrics = regression_metrics(
            y_test,
            neural_predictions,
        )

        all_results.append(
            {
                "specification": specification_name,
                "model": "Neural network",
                **neural_metrics,
            }
        )

        # -----------------------------------------------------
        # Save predictions for each specification
        # -----------------------------------------------------
        output_name = (
            specification_name
            .lower()
            .replace("/", "_")
            .replace(" ", "_")
        )

        predictions_output[
            f"{output_name}_ridge_prediction"
        ] = baseline_predictions

        predictions_output[
            f"{output_name}_neural_prediction"
        ] = neural_predictions

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------
    results = pd.DataFrame(
        all_results
    )

    os.makedirs(
        "data/model_output",
        exist_ok=True,
    )

    results.to_csv(
        "data/model_output/"
        "model_metrics_feature_comparison.csv",
        index=False,
    )

    predictions_output.to_csv(
        "data/model_output/"
        "predictions_feature_comparison.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # Console output
    # ---------------------------------------------------------
    print(
        f"\nObservations: {len(data)}"
    )

    print(
        f"Training observations: {split_index} | "
        f"Test observations: "
        f"{len(data) - split_index}"
    )

    print(
        "\nOut-of-sample model performance:"
    )

    print(
        results.to_string(
            index=False
        )
    )

    print(
        "\nResults saved to:\n"
        "data/model_output/"
        "model_metrics_feature_comparison.csv\n"
        "data/model_output/"
        "predictions_feature_comparison.csv"
    )


if __name__ == "__main__":
    main()