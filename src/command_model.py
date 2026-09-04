from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import LogisticRegression

from hm3d_dataset_builder import load_jsonl


TEXT_COL = "instruction_vi"


def load_episode_frame(path: str | Path) -> pd.DataFrame:
    rows = load_jsonl(path)
    if not rows:
        raise ValueError(f"No episodes found in {path}")
    df = pd.DataFrame(rows)
    df["needs_clarification_label"] = df["needs_clarification"].astype(str)
    df["item_label"] = df["item"].fillna("").replace("", "UNKNOWN_ITEM")
    df["goal_label"] = df["goal_description"].fillna("UNKNOWN_GOAL")
    return df


def _text_column(values: Any):
    if isinstance(values, pd.DataFrame):
        return values[TEXT_COL]
    return values


def make_text_classifier() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "text",
                FunctionTransformer(_text_column, validate=False),
            ),
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    min_df=1,
                    lowercase=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train_single_task(df: pd.DataFrame, label_col: str):
    train_df, test_df = train_test_split(
        df,
        test_size=0.25,
        random_state=7,
        stratify=df[label_col] if df[label_col].nunique() > 1 else None,
    )
    model = make_text_classifier()
    model.fit(train_df[[TEXT_COL]], train_df[label_col])
    pred = model.predict(test_df[[TEXT_COL]])
    metrics = {
        "label": label_col,
        "accuracy": float(accuracy_score(test_df[label_col], pred)),
        "classification_report": classification_report(
            test_df[label_col],
            pred,
            zero_division=0,
        ),
        "test_size": int(len(test_df)),
        "train_size": int(len(train_df)),
    }
    return model, metrics


def train_command_models(
    episode_jsonl: str | Path,
    output_dir: str | Path,
    labels: tuple[str, ...] = (
        "needs_clarification_label",
        "item_label",
        "goal_label",
    ),
) -> dict[str, Any]:
    df = load_episode_frame(episode_jsonl)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifact: dict[str, Any] = {
        "models": {},
        "labels": labels,
        "source_episode_jsonl": str(episode_jsonl),
    }
    metrics: dict[str, Any] = {}

    for label in labels:
        if df[label].nunique() < 2:
            metrics[label] = {
                "skipped": True,
                "reason": "Need at least two classes for training.",
            }
            continue
        model, label_metrics = train_single_task(df, label)
        artifact["models"][label] = model
        metrics[label] = label_metrics

    model_file = output_path / "command_model.joblib"
    metrics_file = output_path / "command_model_metrics.json"

    joblib.dump(artifact, model_file)
    metrics_file.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "model_file": str(model_file),
        "metrics_file": str(metrics_file),
        "metrics": metrics,
    }


def load_command_models(model_file: str | Path) -> dict[str, Any]:
    return joblib.load(model_file)


def predict_command(model_file: str | Path, instruction_vi: str) -> dict[str, str]:
    artifact = load_command_models(model_file)
    row = pd.DataFrame([{TEXT_COL: instruction_vi}])
    outputs: dict[str, str] = {}
    for label, model in artifact["models"].items():
        outputs[label] = str(model.predict(row[[TEXT_COL]])[0])
    return outputs
