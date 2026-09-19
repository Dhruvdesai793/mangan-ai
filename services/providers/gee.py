"""Google Earth Engine feature provider with explicit, disclosed demo fallback."""
from __future__ import annotations

import hashlib
import logging
import random
from dataclasses import dataclass
from typing import Any

from config import Settings, get_settings
from services.providers.moil_reference import MoilReferenceProvider

LOGGER = logging.getLogger(__name__)
PIPELINE_VERSION = "gee_s2_srtm_v001"


@dataclass(frozen=True)
class FeatureVector:
    features: dict[str, Any]
    data_source: str
    limitation: str | None = None


class GeeProvider:
    def __init__(self, settings: Settings | None = None, reference: MoilReferenceProvider | None = None) -> None:
        self.settings = settings or get_settings()
        self.reference = reference or MoilReferenceProvider()
        self._initialized = False

    def initialize(self) -> None:
        if not self.settings.gee_enabled:
            raise RuntimeError("Google Earth Engine is disabled")
        if not self.settings.gee_project_id:
            raise RuntimeError("GEE_PROJECT_ID is required when GEE_ENABLED=true")
        import ee
        ee.Initialize(project=self.settings.gee_project_id)
        self._initialized = True

    def extract(self, site_id: str) -> FeatureVector:
        try:
            if not self._initialized:
                self.initialize()
            return FeatureVector(self._extract_gee(site_id), "GOOGLE_EARTH_ENGINE")
        except Exception as exc:
            LOGGER.warning("GEE extraction unavailable for %s: %s", site_id, exc)
            if not self.settings.gee_allow_demo_features:
                raise
            return FeatureVector(
                self._demo_features(site_id),
                "DEMO_GEE_FALLBACK",
                f"Earth Engine extraction was unavailable ({type(exc).__name__}); explicitly enabled demo features were used.",
            )

    def _extract_gee(self, site_id: str) -> dict[str, Any]:
        import ee
        lease = self.reference.leases_for_site(site_id)
        if not lease["features"]:
            raise ValueError(f"no verified lease geometry exists for {site_id}")
        aoi = ee.Geometry(lease["features"][0]["geometry"])

        def mask_clouds(image):
            qa = image.select("QA60")
            mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
            return image.updateMask(mask).divide(10000)

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(self.settings.gee_start_date, self.settings.gee_end_date)
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", self.settings.gee_cloud_percent))
            .map(mask_clouds)
        )
        if int(collection.size().getInfo()) == 0:
            raise RuntimeError("no cloud-filtered Sentinel-2 images matched the configured period")
        composite = collection.median()
        ndvi = composite.normalizedDifference(["B8", "B4"]).rename("ndvi")
        ndmi = composite.normalizedDifference(["B8", "B11"]).rename("ndmi")
        dem = ee.Image("USGS/SRTMGL1_003").select("elevation").rename("elevation_m")
        slope = ee.Terrain.slope(dem).rename("slope_deg")
        # Curvature is derived from the DEM Laplacian at the aggregation scale.
        curvature = dem.convolve(ee.Kernel.laplacian8()).rename("curvature")
        image = composite.select(["B2", "B3", "B4", "B8", "B11", "B12"], [
            "sentinel2_b2", "sentinel2_b3", "sentinel2_b4", "sentinel2_b8", "sentinel2_b11", "sentinel2_b12",
        ]).addBands([ndvi, ndmi, dem, slope, curvature])
        values = image.reduceRegion(
            reducer=ee.Reducer.median(), geometry=aoi, scale=30, bestEffort=True, maxPixels=10_000_000,
        ).getInfo()
        required = ["sentinel2_b2", "sentinel2_b3", "sentinel2_b4", "sentinel2_b8", "sentinel2_b11", "sentinel2_b12", "ndvi", "ndmi", "elevation_m", "slope_deg", "curvature"]
        missing = [name for name in required if values.get(name) is None]
        if missing:
            raise RuntimeError(f"GEE result missing values: {missing}")
        values["geology_class"] = self._geology_class(site_id)
        return {name: float(values[name]) if name != "geology_class" else values[name] for name in [*required, "geology_class"]}

    def _geology_class(self, site_id: str) -> str:
        for row in self.reference._read("moil_site_catalog.csv"):
            if row["site_id"] == site_id:
                source = f'{row.get("host_lithology", "")} {row.get("geology_unit", "")}'.lower()
                if "gondite" in source: return "gondite"
                if "laterite" in source: return "laterite"
                if "iron" in source: return "banded_iron_formation"
        return "unknown"

    def _demo_features(self, site_id: str) -> dict[str, Any]:
        mine = self.reference.get_mine(site_id)
        if mine is None:
            raise ValueError(f"unknown site_id: {site_id}")
        seed = int(hashlib.sha256(site_id.encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)
        def jitter(value: float, scale: float) -> float: return round(value + rng.uniform(-scale, scale), 6)
        return {
            "sentinel2_b2": max(0.0, jitter(0.08, 0.012)), "sentinel2_b3": max(0.0, jitter(0.10, 0.012)),
            "sentinel2_b4": max(0.0, jitter(0.13, 0.015)), "sentinel2_b8": max(0.0, jitter(0.25, 0.025)),
            "sentinel2_b11": max(0.0, jitter(0.31, 0.025)), "sentinel2_b12": max(0.0, jitter(0.23, 0.02)),
            "ndvi": min(1.0, max(-1.0, jitter(0.20, 0.08))), "ndmi": min(1.0, max(-1.0, jitter(0.04, 0.05))),
            "elevation_m": jitter(330.0, 50.0), "slope_deg": max(0.0, jitter(11.0, 4.0)),
            "curvature": jitter(0.1, 0.25), "geology_class": self._geology_class(site_id),
        }
