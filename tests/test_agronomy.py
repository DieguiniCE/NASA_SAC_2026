import copy
import json
import math
import unittest
from datetime import date
from unittest.mock import patch, Mock
from src.models.sensitivity_viability_model import SensitivityViabilityModel as Model
from src.data.crops_catalog import CROPS_LIST, get_crop_by_name
from src.services.nasa_power import (MONTH_KEYS, _generate_synthetic_cr_climatology,
    parse_power_climatology, fetch_nasa_power_climatology, fetch_power_monthly_history)
from src.services.rotation_service import RotationAnalysisService as Rotation, MULTI_STRATEGY_CATALOG
from src.services.seasonal_risk_service import build_seasonal_alerts
from src.services.vegetation_index_service import summarize_ndvi, summarize_canopy, coverage_factor
from src.services.imn_cr_service import calculate_frost_risk
from src.services.data_lake import get_unified_environmental_profile
from src.services.gpm_service import GPMService


def environment(lat=9.9281, lon=-84.0907):
    climate = _generate_synthetic_cr_climatology(lat, lon)
    with patch("src.services.data_lake.fetch_nasa_power_climatology", return_value=climate), \
         patch("src.services.data_lake.fetch_power_monthly_history", return_value={"records": [], "source": "fixture", "period": "2021-2025"}), \
         patch("src.services.data_lake.get_vegetation_profile", return_value={
             "ndvi": summarize_ndvi([]), "canopy": summarize_canopy(None, None), "status": "not_configured"}):
        return get_unified_environmental_profile(lat, lon)


def power_response():
    params = {k: {m: value for m in MONTH_KEYS} for k, value in
              {"T2M": 24, "T2M_MAX": 29, "T2M_MIN": 19, "PRECTOTCORR": 5,
               "RH2M": 80, "WS2M": 3}.items()}
    return {"properties": {"parameter": params},
            "parameters": {"PRECTOTCORR": {"units": "mm/day"}},
            "geometry": {"coordinates": [-84, 10, 0]}, "header": {"range": "2001-2025"}}


class ViabilityTests(unittest.TestCase):
    def score(self, crop="Coffee", temp=20, rain=2000, alt=1250, moisture=.3, **kwargs):
        return Model.calculate_viability(get_crop_by_name(crop), temp, rain, alt, moisture,
                                         "Inceptisol", **kwargs)

    def test_ideal_conditions_for_every_crop(self):
        for c in CROPS_LIST:
            r = Model.calculate_viability(c, c["ideal_temp_c"]["sweet_spot"],
                c["precipitation_mm"]["sweet_spot"], c["altitude_m"]["sweet_spot"],
                c["soil_moisture_m3_m3"]["sweet_spot"], c["soil_type"][0])
            self.assertEqual(r["success_percentage"], 100)

    def test_weights_applied_and_sum_to_one(self):
        r = self.score(temp=25, rain=3300)
        self.assertAlmostEqual(sum(r["weights"].values()), 1)
        self.assertAlmostEqual(r["penalties"]["temp"],
            (100 - r["factor_scores"]["temp"]) * .45, delta=.1)

    def test_no_penalty_inside_ideal_interval(self):
        self.assertEqual(self.score(temp=17, rain=1000)["success_percentage"], 100)
        self.assertEqual(self.score(temp=23, rain=3000)["success_percentage"], 100)

    def test_smooth_boundary(self):
        a = Model.factor_suitability(23, {"min": 17, "max": 23}, 3)
        b = Model.factor_suitability(23.0001, {"min": 17, "max": 23}, 3)
        self.assertAlmostEqual(a, b, places=5)

    def test_heat_stress_monotonic(self):
        scores = [self.score(temp=t)["success_percentage"] for t in (23, 25, 28, 32, 40)]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertLess(scores[-1], 40)

    def test_drought_stress_and_irrigation(self):
        dry = self.score(rain=300, moisture=.1)["success_percentage"]
        watered = self.score(rain=300, moisture=.1, irrigation=True)["success_percentage"]
        self.assertGreater(watered, dry)
        self.assertLess(watered, 100)

    def test_irrigation_does_not_fix_excess_water(self):
        self.assertEqual(self.score(rain=6000, moisture=.7)["success_percentage"],
                         self.score(rain=6000, moisture=.7, irrigation=True)["success_percentage"])

    def test_shade_only_coffee_and_not_cold_conditions(self):
        self.assertGreater(self.score(temp=28, shade=True)["success_percentage"],
                           self.score(temp=28)["success_percentage"])
        self.assertEqual(self.score(temp=15, shade=True)["success_percentage"],
                         self.score(temp=15)["success_percentage"])
        self.assertEqual(self.score("Banana", temp=35, shade=True)["success_percentage"],
                         self.score("Banana", temp=35)["success_percentage"])

    def test_elevation_cannot_alone_reject_lowland_cane(self):
        self.assertGreaterEqual(self.score("Sugar Cane", temp=28, rain=1800, alt=20, moisture=.28)["success_percentage"], 80)

    def test_pineapple_wet_tropics_requires_unsaturated_soil(self):
        suitable = self.score("Pineapple", temp=27, rain=3000, alt=100, moisture=.28)
        saturated = self.score("Pineapple", temp=27, rain=3000, alt=100, moisture=.70)
        self.assertGreaterEqual(suitable["success_percentage"], 60)
        self.assertLess(saturated["success_percentage"], 40)

    def test_invalid_environment_rejected(self):
        for value in (None, float("nan"), float("inf"), -999):
            with self.assertRaises((ValueError, TypeError)):
                self.score(temp=value)

    def test_zero_scenario_identity(self):
        self.assertEqual(self.score(), self.score(delta_temp_c=0, delta_precip_pct=0))

    def test_scenario_not_mutating_input(self):
        before = copy.deepcopy(CROPS_LIST)
        self.score(delta_temp_c=4, delta_precip_pct=-40)
        self.assertEqual(before, CROPS_LIST)

    def test_uncertainty_brackets_score_and_labels_method(self):
        r = self.score(temp=26)
        u = r["uncertainty"]
        self.assertLessEqual(u["lower"], r["success_percentage"])
        self.assertGreaterEqual(u["upper"], r["success_percentage"])
        self.assertIn("no intervalo", u["kind"])
        observed = self.score(temp=26, data_quality="observed")["uncertainty"]
        self.assertGreaterEqual(u["margin_points"], observed["margin_points"])

    def test_representative_sites_have_candidates(self):
        for args in ((20, 2000, 1250, .3, "Andisol"), (27, 3000, 50, .35, "Inceptisol"),
                     (28, 1600, 100, .25, "Vertisol"), (18, 1800, 2000, .29, "Ultisol")):
            results = Model.calculate_all_crops(*args)
            self.assertTrue(any(r["success_percentage"] >= 60 for r in results))
            self.assertTrue(all(0 <= r["success_percentage"] <= 100 for r in results))


class NasaTests(unittest.TestCase):
    def test_rain_units_and_sea_level_elevation(self):
        r = parse_power_climatology(power_response(), 10, -84)
        self.assertEqual(r["annual_summary"]["annual_precipitation_mm"], 1825)
        self.assertEqual(r["elevation_m"], 0)

    def test_hourly_units_converted(self):
        raw = power_response()
        raw["parameters"]["PRECTOTCORR"]["units"] = "mm/hour"
        for m in MONTH_KEYS:
            raw["properties"]["parameter"]["PRECTOTCORR"][m] = 5 / 24
        self.assertEqual(parse_power_climatology(raw,10,-84)["annual_summary"]["annual_precipitation_mm"], 1825)

    def test_missing_and_fill_values_not_zero_rain(self):
        for value in (None, -999, float("nan")):
            raw = power_response()
            raw["properties"]["parameter"]["PRECTOTCORR"]["JAN"] = value
            with self.assertRaises(ValueError):
                parse_power_climatology(raw, 10, -84)

    def test_missing_temperature_not_defaulted(self):
        raw = power_response()
        del raw["properties"]["parameter"]["T2M"]["JAN"]
        with self.assertRaises(ValueError):
            parse_power_climatology(raw, 10, -84)

    def test_numeric_month_keys(self):
        raw = power_response()
        for k, monthly in raw["properties"]["parameter"].items():
            raw["properties"]["parameter"][k] = {str(i): monthly[m] for i,m in enumerate(MONTH_KEYS,1)}
        self.assertEqual(parse_power_climatology(raw,10,-84)["annual_summary"]["annual_precipitation_mm"],1825)

    def test_bad_api_data_falls_back_with_provenance(self):
        response = Mock()
        response.json.return_value = {"properties": {"parameter": {}}}
        with patch("src.services.nasa_power.requests.get", return_value=response):
            result = fetch_nasa_power_climatology(10,-84)
        self.assertTrue(result["is_simulated"])
        self.assertEqual(result["fallback_reason"], "ValueError")

    def test_monthly_history_excludes_annual_and_uses_leap_days(self):
        response = Mock()
        response.json.return_value = {"properties": {"parameter": {
            "T2M": {"202402": 20, "202413": 20},
            "PRECTOTCORR": {"202402": 2, "202413": 2},
            "WS2M": {"202402": -999}, "T2M_MIN": {"202402": 10}}}}
        with patch("src.services.nasa_power.requests.get", return_value=response):
            data = fetch_power_monthly_history(10,-84, years=1, today=date(2025,1,1))
        self.assertEqual(len(data["records"]),1)
        self.assertEqual(data["records"][0]["precipitation_mm"],58)
        self.assertIsNone(data["records"][0]["wind_m_s"])

    def test_regional_rainfall_preserves_total(self):
        for lat, lon in ((10.5,-85.5),(10.5,-83.5),(8.8,-83.5),(9.9,-84.4)):
            r=GPMService.get_precipitation_profile(lat,lon,base_annual_mm=2000)
            self.assertAlmostEqual(r["annual_precipitation_mm"],2000,delta=1)


class RotationTests(unittest.TestCase):
    def evaluate(self, **changes):
        options = dict(primary_crop="Coffee", primary_viability=0, actual_temp_c=20,
            actual_precip_mm=2000, actual_altitude_m=1250, actual_soil_moisture_m3_m3=.3)
        options.update(changes)
        return Rotation.evaluate_rotation_strategies(**options)

    def test_single_scenario_and_consistent_baseline(self):
        r=self.evaluate(delta_temp_c=4, delta_precip_pct=-40)
        direct=Model.calculate_viability(get_crop_by_name("Coffee"),20,2000,1250,.3,
                                        delta_temp_c=4,delta_precip_pct=-40)
        self.assertEqual(r["baseline_viability"],direct["success_percentage"])
        self.assertEqual(r["strategies"][0]["viability_score"],r["baseline_viability"])

    def test_no_forced_minimum_or_false_recommendation(self):
        r=self.evaluate(actual_temp_c=50,actual_precip_mm=0,actual_soil_moisture_m3_m3=0)
        self.assertFalse(r["recommendation_available"])
        self.assertTrue(all(s["viability_score"] < 40 for s in r["strategies"]))
        self.assertTrue(all(not s["is_top_recommendation"] for s in r["strategies"]))

    def test_net_advantage_is_difference_in_points(self):
        r=self.evaluate()
        for s in r["strategies"]:
            self.assertEqual(s["net_advantage_vs_baseline"],s["viability_score"]-r["baseline_viability"])

    def test_priority_changes_alignment_without_changing_aptitude(self):
        water={s["strategy_id"]:s for s in self.evaluate(farmer_priority="water_conservation")["strategies"]}
        income={s["strategy_id"]:s for s in self.evaluate(farmer_priority="income")["strategies"]}
        self.assertTrue(any(water[k]["farmer_alignment_score"] != income[k]["farmer_alignment_score"] for k in water))
        self.assertTrue(all(water[k]["viability_score"] == income[k]["viability_score"] for k in water))

    def test_catalog_not_mutated(self):
        before=copy.deepcopy(MULTI_STRATEGY_CATALOG)
        self.evaluate(delta_temp_c=4)
        self.assertEqual(before,MULTI_STRATEGY_CATALOG)

    def test_unknown_crop_and_priority(self):
        with self.assertRaises(ValueError): self.evaluate(primary_crop="Unknown")
        with self.assertRaises(ValueError): self.evaluate(farmer_priority="Unknown")

    def test_calendar_uses_local_monthly_pattern(self):
        climate={"PRECTOT_MONTHLY":{m:250 for m in MONTH_KEYS},"T2M":{m:26 for m in MONTH_KEYS}}
        r=self.evaluate(monthly_climate=climate,delta_precip_pct=-20)
        self.assertTrue(all(m["precipitation_mm"]==200 for m in r["vulnerability_calendar"]))
        self.assertTrue(all(m["bare_soil_monoculture_index"] is None for m in r["vulnerability_calendar"]))


class RiskTests(unittest.TestCase):
    def setUp(self):
        self.env=environment(10.6,-85.45)

    def test_next_months_roll_into_new_year(self):
        rows=build_seasonal_alerts(self.env,today=date(2026,11,15))["months"]
        self.assertEqual([r["month"] for r in rows],["2026-12","2027-01","2027-02","2027-03","2027-04","2027-05"])

    def test_dry_season_has_drought_and_wind_risk(self):
        rows=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"]
        self.assertGreaterEqual(rows[0]["drought_score"],65)
        self.assertGreaterEqual(rows[0]["wind_erosion_score"],35)

    def test_no_wind_means_unknown_wind_risk(self):
        self.env["raw_services"]["nasa_power"]["parameters"]["WS2M"]={}
        rows=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"]
        self.assertTrue(all(r["wind_erosion_score"] is None for r in rows))

    def test_historical_frequency_requires_three_years(self):
        records=[{"year":y,"month":1,"precipitation_mm":0,"temperature_c":28,"wind_m_s":6} for y in (2023,2024,2025)]
        self.env["climate_history"]["records"]=records
        row=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"][0]
        self.assertEqual(row["historical_years"],3)
        self.assertEqual(row["historical_high_risk_frequency_pct"]["drought"],100)
        self.env["climate_history"]["records"]=records[:2]
        row=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"][0]
        self.assertIsNone(row["historical_high_risk_frequency_pct"]["drought"])

    def test_bare_soil_increases_rain_erosion(self):
        p=self.env["raw_services"]["nasa_power"]["parameters"]
        p["PRECTOT_MONTHLY"]["JAN"]=400
        self.env["vegetation"]["ndvi"]["records"]=[{"date":"2025-01-01","ndvi":.1}]
        bare=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"][0]
        self.env["vegetation"]["ndvi"]["records"]=[{"date":"2025-01-01","ndvi":.8}]
        covered=build_seasonal_alerts(self.env,today=date(2026,12,15))["months"][0]
        self.assertGreater(bare["water_erosion_score"],covered["water_erosion_score"])

    def test_frost_does_not_double_count_altitude(self):
        self.assertEqual(calculate_frost_risk(10,2000)["adjusted_min_c"],10)
        self.assertEqual(calculate_frost_risk(10,2000,1000)["adjusted_min_c"],4)

    def test_frost_thresholds(self):
        self.assertEqual(calculate_frost_risk(8.1,2000)["color"],"green")
        self.assertEqual(calculate_frost_risk(8,2000)["color"],"orange")
        self.assertEqual(calculate_frost_risk(4,2000)["color"],"red")

    def test_vegetation_quality_and_negative_ndvi(self):
        result=summarize_ndvi([{"date":"2025-01-01","ndvi":.1,"quality_ok":False},
                               {"date":"2025-02-01","ndvi":-.1,"quality_ok":True}])
        self.assertEqual(len(result["records"]),1)
        self.assertTrue(result["records"][0]["exposed_soil_risk"])
        self.assertIsNone(coverage_factor(None))

    def test_gedi_no_footprints_is_not_open_field(self):
        self.assertEqual(summarize_canopy(None,None)["status"],"unavailable")
        self.assertFalse(summarize_canopy(None,None)["canopy_detected"])
        self.assertTrue(summarize_canopy(12,80)["canopy_detected"])
        self.assertFalse(summarize_canopy(12,80,quality_ok=False)["canopy_detected"])


if __name__ == "__main__":
    unittest.main()
