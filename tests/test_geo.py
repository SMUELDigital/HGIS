import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from hgis.geo import haversine_distance


def test_haversine_distance():
    # Distance between Paris (48.8566, 2.3522) and London (51.5074, -0.1278)
    dist = haversine_distance(48.8566, 2.3522, 51.5074, -0.1278)
    assert 340 < dist < 350
