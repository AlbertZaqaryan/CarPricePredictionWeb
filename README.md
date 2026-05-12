# CarPricePredictionWeb

A simple end-to-end machine-learning web app that predicts the **market price of a used car** from its features. The model is a `scikit-learn` Linear Regression trained on a small Kaggle-style listings dataset, and it is served behind a **Django** backend with a modern HTML / CSS / vanilla-JS front end.

---

## Demo flow

1. User opens the page and fills in the car details (brand, year, fuel, engine, mileage, body, color, status).
2. The browser sends a JSON request to `/predict/`.
3. Django loads `model.pkl`, label-encodes the categorical inputs the same way the notebook did, builds a feature row, and calls `model.predict(...)`.
4. The predicted price is animated back into the page.

---

## Features

- Modern, responsive UI (glassy card, gradient orbs, dark theme).
- AJAX form submission with a smooth count-up animation on the result.
- Strict, server-side feature validation (unknown brand / fuel / etc. returns a clean JSON error).
- Mileage entered as **km** or **miles** (miles are converted to km, exactly like training).
- Model is loaded **once at process start**, not on every request.

---

## Tech stack

| Layer      | Tools                                                         |
|------------|---------------------------------------------------------------|
| ML         | Python, NumPy, pandas, scikit-learn (`LinearRegression`, `LabelEncoder`) |
| Notebook   | Jupyter (`ai/Untitled.ipynb`)                                 |
| Backend    | Django 5                                                      |
| Frontend   | HTML, CSS (custom, no framework), vanilla JavaScript          |
| Storage    | SQLite (default, unused for predictions)                      |

---

## Project structure

```
car_price_parser_web_ai/
├── ai/                          # Data + training notebook
│   ├── train.csv
│   ├── test.csv
│   ├── sample_submission.csv
│   └── Untitled.ipynb           # Trains the LinearRegression and writes model.pkl
│
└── core/                        # Django project
    ├── manage.py
    ├── db.sqlite3
    ├── core/                    # Django settings package
    │   ├── settings.py
    │   ├── urls.py
    │   └── ...
    └── main/                    # The single Django app
        ├── model.pkl            # Trained scikit-learn model
        ├── views.py             # index view + /predict/ JSON endpoint
        ├── urls.py
        ├── templates/
        │   └── index.html       # Form UI
        └── static/
            ├── css/style.css    # Modern dark theme
            └── js/script.js     # AJAX submit + animated result
```

---

## The model

Trained in `ai/Untitled.ipynb` on `train.csv` (~1.6k rows).

**Features used (in this order):**

| # | Feature        | Type        | Preprocessing                                                  |
|---|----------------|-------------|----------------------------------------------------------------|
| 1 | `model`        | categorical | `LabelEncoder` — `hyundai, kia, mercedes-benz, nissan, toyota` |
| 2 | `year`         | numeric     | —                                                              |
| 3 | `motor_type`   | categorical | `LabelEncoder` — `diesel, gas, hybrid, petrol, petrol and gas` |
| 4 | `running`      | numeric     | `"X km"` → `X`, `"X miles"` → `X * 1.6`                        |
| 5 | `color`        | categorical | `LabelEncoder` (17 colors)                                     |
| 6 | `type`         | categorical | `LabelEncoder` (7 body types)                                  |
| 7 | `status`       | categorical | `LabelEncoder` — `crashed, excellent, good, new, normal`       |
| 8 | `motor_volume` | numeric     | —                                                              |

`wheel` was dropped during training because the training set contained only `"left"` values.

The fitted `LinearRegression` is pickled to `core/main/model.pkl`.

---

## Getting started

### 1. Clone

```bash
git clone https://github.com/AlbertZaqaryan/CarPricePredictionWeb.git
cd CarPricePredictionWeb
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django pandas numpy scikit-learn
```

> If you re-train the model, make sure the scikit-learn version you use matches the one that produced `model.pkl`, otherwise unpickling can break.

### 4. (Optional) Re-train the model

Open the notebook:

```bash
cd ai
jupyter notebook Untitled.ipynb
```

Run all cells. The last cell saves `model.pkl` — copy it into `core/main/model.pkl`.

### 5. Run the Django server

```bash
cd core
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

---

## API

### `POST /predict/`

Request body (JSON):

```json
{
  "model": "toyota",
  "year": 2022,
  "motor_type": "petrol",
  "motor_volume": 2.0,
  "running": 3000,
  "running_unit": "km",
  "type": "sedan",
  "color": "skyblue",
  "status": "excellent"
}
```

Response (success):

```json
{ "ok": true, "price": 23721.37 }
```

Response (validation error):

```json
{ "ok": false, "error": "Unknown model: 'bmw'" }
```

**Accepted values**

| Field        | Allowed values                                                                                                                          |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `model`      | `hyundai`, `kia`, `mercedes-benz`, `nissan`, `toyota`                                                                                   |
| `motor_type` | `diesel`, `gas`, `hybrid`, `petrol`, `petrol and gas`                                                                                   |
| `type`       | `Coupe`, `Universal`, `hatchback`, `minivan / minibus`, `pickup`, `sedan`, `suv`                                                        |
| `status`     | `crashed`, `excellent`, `good`, `new`, `normal`                                                                                         |
| `color`      | `beige`, `black`, `blue`, `brown`, `cherry`, `clove`, `golden`, `gray`, `green`, `orange`, `other`, `pink`, `purple`, `red`, `silver`, `skyblue`, `white` |
| `running_unit` | `km` (default) or `miles`                                                                                                             |

---

## Notes / limitations

- The dataset is **small (~1.6k rows)** and the model is a plain `LinearRegression`, so predictions are a rough estimate, not a real valuation.
- Categorical features are label-encoded, which imposes an artificial ordinal relationship. A `OneHotEncoder` or a tree-based model (e.g. `RandomForestRegressor` / `XGBoost`) would likely score better.
- `DEBUG = True` and the `SECRET_KEY` is the default dev key — **do not deploy this as-is**. Set `DEBUG = False`, configure `ALLOWED_HOSTS`, and rotate the secret key before publishing.

---

## License

No license file is currently included. Add one (e.g. MIT) if you want to make the project reusable.
