import json
import pickle
from pathlib import Path

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

with open(MODEL_PATH, "rb") as f:
    _MODEL = pickle.load(f)

FEATURE_ORDER = [
    "model",
    "year",
    "motor_type",
    "running",
    "color",
    "type",
    "status",
    "motor_volume",
]

# LabelEncoder uses alphabetical ordering of fitted classes.
# These maps mirror what the notebook produced when training.
MODEL_CHOICES = ["hyundai", "kia", "mercedes-benz", "nissan", "toyota"]
MOTOR_TYPE_CHOICES = ["diesel", "gas", "hybrid", "petrol", "petrol and gas"]
COLOR_CHOICES = [
    "beige", "black", "blue", "brown", "cherry", "clove", "golden", "gray",
    "green", "orange", "other", "pink", "purple", "red", "silver", "skyblue",
    "white",
]
TYPE_CHOICES = [
    "Coupe", "Universal", "hatchback", "minivan / minibus", "pickup", "sedan",
    "suv",
]
STATUS_CHOICES = ["crashed", "excellent", "good", "new", "normal"]


def _encode(value: str, choices: list[str], field: str) -> int:
    try:
        return choices.index(value)
    except ValueError as exc:
        raise ValueError(f"Unknown {field}: {value!r}") from exc


def index(request):
    context = {
        "models": MODEL_CHOICES,
        "motor_types": MOTOR_TYPE_CHOICES,
        "colors": COLOR_CHOICES,
        "types": TYPE_CHOICES,
        "statuses": STATUS_CHOICES,
    }
    return render(request, "index.html", context)


@require_http_methods(["POST"])
def predict(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))

        running_value = float(payload["running"])
        if str(payload.get("running_unit", "km")).lower() == "miles":
            running_value = running_value * 1.6

        row = {
            "model": _encode(payload["model"], MODEL_CHOICES, "model"),
            "year": int(payload["year"]),
            "motor_type": _encode(
                payload["motor_type"], MOTOR_TYPE_CHOICES, "motor_type"
            ),
            "running": running_value,
            "color": _encode(payload["color"], COLOR_CHOICES, "color"),
            "type": _encode(payload["type"], TYPE_CHOICES, "type"),
            "status": _encode(payload["status"], STATUS_CHOICES, "status"),
            "motor_volume": float(payload["motor_volume"]),
        }

        X = pd.DataFrame([[row[f] for f in FEATURE_ORDER]], columns=FEATURE_ORDER)
        price = float(_MODEL.predict(X)[0])
        price = max(price, 0.0)
        return JsonResponse({"ok": True, "price": round(price, 2)})
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
