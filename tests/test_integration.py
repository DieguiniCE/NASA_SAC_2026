import unittest
from unittest.mock import patch
from tests.test_agronomy import environment


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from src.api import app
        cls.client=TestClient(app)
        cls.env=environment()

    def test_response_and_shared_scenario(self):
        with patch("src.api.get_unified_environmental_profile",return_value=self.env):
            response=self.client.get("/api/viability",params={"lat":9.9281,"lon":-84.0907,
                "delta_temp_c":2,"delta_precip_pct":-30,"irrigation":True})
        self.assertEqual(response.status_code,200,response.text)
        body=response.json()
        self.assertEqual(len(body["crops_viability"]),5)
        self.assertEqual(len(body["seasonal_alerts"]["months"]),6)
        self.assertEqual(body["crops_viability"][0]["actual_values"]["temperature_c"],
                         self.env["temperatures"]["air_temperature_mean_c"]+2)
        self.assertTrue(body["scenario"]["irrigation"])

    def test_invalid_scenario_rejected(self):
        response=self.client.get("/api/viability",params={"lat":9.9281,"lon":-84.0907,"delta_precip_pct":-101})
        self.assertEqual(response.status_code,422)

    def test_health_and_catalog(self):
        self.assertEqual(self.client.get("/api/health").status_code,200)
        self.assertEqual(self.client.get("/api/crops").json()["count"],5)


class UiTests(unittest.TestCase):
    def test_pages_and_shared_controls(self):
        from streamlit.testing.v1 import AppTest
        env=environment()
        with patch("src.services.data_lake.get_unified_environmental_profile",return_value=env):
            from pathlib import Path
            at=AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"),default_timeout=30).run()
            self.assertEqual(len(at.exception),0,str(at.exception))
            at.slider(key="scenario_temp").set_value(2.0)
            at.slider(key="scenario_precip").set_value(-30)
            at.checkbox(key="farm_irrigation").check()
            at.run()
            self.assertEqual(len(at.exception),0,str(at.exception))
            for language in ("Español", "English"):
                language_control = next(r for r in at.radio if r.label == "🌐")
                language_control.set_value(language).run()
                navigation = next(r for r in at.radio if r.label == "Página:")
                options = list(navigation.options)
                self.assertEqual(len(options), 4)
                for label in options:
                    navigation = next(r for r in at.radio if r.label == "Página:")
                    navigation.set_value(label).run()
                    self.assertEqual(len(at.exception),0,str(at.exception))
                    self.assertEqual(at.slider(key="scenario_temp").value,2.0)
                    self.assertEqual(at.slider(key="scenario_precip").value,-30)
                    self.assertEqual(next(r for r in at.radio if r.label == "Página:").value, label)



if __name__=="__main__":
    unittest.main()
