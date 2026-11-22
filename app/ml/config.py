"""Fixed model constants (PLAN.md section 5). Do not re-derive these values."""
BUSINESS_TYPES = ("warung", "cafe", "gerobak", "bakery", "kantin")
LOCATION_TYPES = ("kampus", "kantor", "permukiman", "pasar")
CATEGORIES = ("nasi", "mie", "snack", "minuman", "roti")

N_NEIGHBORS = 5
NEIGHBOR_DISTANCE_EPS = 0.1
FALLBACK_MU0 = 10.0
FALLBACK_PHI_DAY = 0.15
PHI_DAY_MIN = 0.02
PHI_DAY_MAX = 1.0
DEFAULT_CAPACITY_FACTOR = 1.0

SHRINKAGE_K = 4
STOCKOUT_UPLIFT = 1.15
CV0 = 0.40
MIN_TARGET_MEAN = 0.5
OWN_WEEKDAY_K = 3

ALPHA_MIN = 0.05
ALPHA_MAX = 0.95
QUANTILE_LEVELS = (0.10, 0.50, 0.90)
NEAREST_BANDS = ("P10", "P50", "P90")
CONFIDENCE_LEVELS = ("rendah", "sedang", "tinggi")
CONFIDENCE_RATIO_LIMIT = 1.2
WEEKDAY_REASON_THRESHOLD = 0.10
WEEKDAY_NAMES = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")

# Reference generator (PLAN.md 5.1), Monday..Sunday.
WEEKDAY_FACTORS = {
    "nasi": (1.00, 1.00, 1.00, 1.02, 1.08, 1.10, 0.80),
    "mie": (1.00, 1.00, 1.00, 1.02, 1.06, 1.12, 0.80),
    "snack": (0.95, 0.95, 0.98, 1.00, 1.10, 1.20, 0.82),
    "minuman": (1.00, 1.00, 1.02, 1.04, 1.10, 1.15, 0.69),
    "roti": (1.02, 1.02, 1.02, 1.04, 1.08, 1.12, 0.70),
}
