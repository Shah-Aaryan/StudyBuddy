"""
retrain_user_behavior_model.py
--------------------------------
Re-creates a “clean” user-behavior RandomForest model that is fully
compatible with the current scikit-learn version in your virtual-env.

Outputs:
    backend/app/ml_models/clean_user_behavior_model.pkl
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib

# ────────────────────────────────────────────────────────────────────────────────
# ⬇️  1.  Model / Feature Extraction Class
# ────────────────────────────────────────────────────────────────────────────────
class UserBehaviorTracker:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            "idle_time_seconds",
            "tab_switches_per_minute",
            "mouse_movement_variance",
            "video_scrub_count",
            "video_replay_count",
            "session_duration_minutes",
            "click_frequency",
            "scroll_speed_variance",
            "page_dwell_time",
            "error_encounters",
        ]

    # ────────────── helpers ──────────────
    def _calculate_idle_time(self, timestamps):
        if len(timestamps) < 2:
            return 0
        idle_secs = [
            (timestamps[i] - timestamps[i - 1]).total_seconds()
            for i in range(1, len(timestamps))
            if (timestamps[i] - timestamps[i - 1]).total_seconds() > 5
        ]
        return sum(idle_secs)

    def _calculate_mouse_variance(self, mouse_moves):
        if len(mouse_moves) < 2:
            return 0
        xs = [e["x"] for e in mouse_moves]
        ys = [e["y"] for e in mouse_moves]
        return np.var(xs) + np.var(ys)

    def _calculate_scroll_variance(self, scroll_events):
        if len(scroll_events) < 2:
            return 0
        speeds = []
        for i in range(1, len(scroll_events)):
            dt = (
                scroll_events[i]["timestamp"] - scroll_events[i - 1]["timestamp"]
            ).total_seconds()
            if dt > 0:
                speeds.append(abs(scroll_events[i]["delta_y"]) / dt)
        return np.var(speeds) if len(speeds) > 1 else 0

    # ────────────── feature extraction ──────────────
    def extract_features(self, interaction_data):
        idle = self._calculate_idle_time(interaction_data["timestamps"])

        events = interaction_data["events"]
        session_minutes = max(interaction_data["session_duration_minutes"], 1)

        tab_switches = sum(e["type"] == "tab_switch" for e in events)
        tab_per_min = tab_switches / session_minutes

        mouse_moves = [e for e in events if e["type"] == "mouse_move"]
        mouse_var = self._calculate_mouse_variance(mouse_moves)

        v_scrub = sum(e["type"] == "video_scrub" for e in events)
        v_replay = sum(e["type"] == "video_replay" for e in events)

        clicks = sum(e["type"] == "click" for e in events)
        click_freq = clicks / session_minutes

        scroll_events = [e for e in events if e["type"] == "scroll"]
        scroll_var = self._calculate_scroll_variance(scroll_events)

        dwell = interaction_data.get("page_dwell_time", 0)
        errors = sum(e["type"] == "error" for e in events)

        return [
            idle,
            tab_per_min,
            mouse_var,
            v_scrub,
            v_replay,
            session_minutes,
            click_freq,
            scroll_var,
            dwell,
            errors,
        ]

    # ────────────── training / saving ──────────────
    def train(self, sessions):
        X, y = [], []
        for s in sessions:
            X.append(self.extract_features(s["interaction_data"]))
            y.append(s["behavior_label"])

        X = np.array(X)
        y = np.array(y)

        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_tr_sc = self.scaler.fit_transform(X_tr)
        X_te_sc = self.scaler.transform(X_te)

        self.model.fit(X_tr_sc, y_tr)

        print("\nModel performance on hold-out set:")
        print(classification_report(y_te, self.model.predict(X_te_sc)))

    def save(self, path):
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": self.feature_names,
            },
            path,
        )
        print(f"✅ Model saved to {path}")


# ────────────────────────────────────────────────────────────────────────────────
# ⬇️  2.  Synthetic Data Generator (identical to your earlier code)
# ────────────────────────────────────────────────────────────────────────────────
def generate_synthetic_dataset(n_samples=1000):
    np.random.seed(42)
    dataset = []

    behavior_defs = {
        "engaged":  dict(idle=(0, 30),  tabs=(0, 2),   mouse=(100, 1000),  scrubs=(0, 2),  replays=(0, 1),
                         dur=(5, 60),  clicks=(2, 10), err=(0, 1)),
        "confused": dict(idle=(30, 120), tabs=(2, 8),  mouse=(1000, 5000), scrubs=(3, 10), replays=(2, 5),
                         dur=(10, 45), clicks=(1, 5), err=(1, 3)),
        "frustrated": dict(idle=(5, 60), tabs=(5, 15), mouse=(3000, 10000), scrubs=(5, 20), replays=(3, 10),
                           dur=(2, 30), clicks=(0.5, 3), err=(2, 5)),
        "about_to_leave": dict(idle=(60, 300), tabs=(8, 20), mouse=(50, 500), scrubs=(0, 5), replays=(0, 2),
                               dur=(1, 15), clicks=(0, 2), err=(1, 4)),
    }

    for _ in range(n_samples):
        label = np.random.choice(list(behavior_defs))
        p = behavior_defs[label]

        dur = np.random.uniform(*p["dur"])
        timestamps = []
        t = datetime.utcnow()
        for _ in range(int(dur * 2)):
            t += timedelta(seconds=np.random.exponential(15))
            timestamps.append(t)

        events = []
        for ts in timestamps:
            e_type = np.random.choice(
                ["click", "mouse_move", "scroll", "tab_switch", "video_scrub", "video_replay", "error"]
            )
            events.append(
                {
                    "type": e_type,
                    "timestamp": ts,
                    "x": np.random.randint(0, 1920) if e_type == "mouse_move" else None,
                    "y": np.random.randint(0, 1080) if e_type == "mouse_move" else None,
                    "delta_y": np.random.randint(-100, 100) if e_type == "scroll" else None,
                }
            )

        dataset.append(
            {
                "interaction_data": {
                    "session_duration_minutes": dur,
                    "timestamps": timestamps,
                    "events": events,
                    "page_dwell_time": np.random.uniform(10, dur * 60),
                },
                "behavior_label": label,
            }
        )
    return dataset


# ────────────────────────────────────────────────────────────────────────────────
# ⬇️  3.  Run training + save
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀  Generating synthetic data...")
    data = generate_synthetic_dataset(1000)

    tracker = UserBehaviorTracker()
    print("🔧  Training model...")
    tracker.train(data)

    # Ensure the output directory exists
    output_path = os.path.join(
        os.path.dirname(__file__), "clean_user_behavior_model.pkl"
    )
    tracker.save(output_path)
