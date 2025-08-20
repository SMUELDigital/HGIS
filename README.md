# HGIS

A minimal Python library for geographic calculations. Currently provides a function to compute great-circle distances using the Haversine formula.

## Usage

```python
from hgis.geo import haversine_distance

# Distance between Paris and London
km = haversine_distance(48.8566, 2.3522, 51.5074, -0.1278)
print(f"Distance: {km:.2f} km")
```

## Development

Install dependencies and run tests with `pytest`:

```bash
pip install -r requirements.txt  # if requirements file exists
pytest
```
