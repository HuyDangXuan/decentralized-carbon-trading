import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.validate_metadata import load_json, validate_metadata, SCHEMA_PATH


class MetadataValidationTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(SCHEMA_PATH)
        self.sample = copy.deepcopy(self.schema["$defs"]["example_verra_vcs"]["const"])

    def test_all_published_examples_pass(self):
        for item in self.schema["$defs"].values():
            self.assertEqual(validate_metadata(item["const"]), [])
        for path in (SCHEMA_PATH.parent / "examples").glob("*.json"):
            self.assertEqual(validate_metadata(load_json(path)), [])

    def test_duplicate_keys_are_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate.json"
            path.write_text('{"properties":{"asset_class":"a","asset_class":"b"}}')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_json(path)

    def test_wrong_units_and_decimals_rejected(self):
        for key, value in [("decimals", 3), ("unit", "kgCO2e"), ("price_unit", "ETH"), ("price_decimals", 18)]:
            with self.subTest(key=key):
                sample = copy.deepcopy(self.sample)
                sample[key] = value
                self.assertTrue(validate_metadata(sample))

    def test_zero_fractional_and_overflow_amounts_rejected(self):
        for amount in [0, -1, 0.5, 2**128]:
            self.sample["properties"]["total_issued_tCO2e"] = amount
            self.assertTrue(validate_metadata(self.sample))

    def test_buffer_boundaries_and_basis_points(self):
        for rate in [10, 15.25, 20]:
            self.sample["properties"]["permanence_risk_buffer"] = rate
            self.assertEqual(validate_metadata(self.sample), [])
        for rate in [0, 9.99, 20.01, 100, 15.001]:
            self.sample["properties"]["permanence_risk_buffer"] = rate
            self.assertTrue(validate_metadata(self.sample))

    def test_required_business_fields(self):
        for field in ["methodology", "country", "region", "additionality", "permanence_risk_buffer"]:
            sample = copy.deepcopy(self.sample)
            del sample["properties"][field]
            self.assertTrue(validate_metadata(sample))

    def test_gold_standard_requires_sdgs_but_verra_does_not(self):
        gold = copy.deepcopy(self.schema["$defs"]["example_gold_standard"]["const"])
        gold["properties"].pop("sdg_contributions")
        self.assertTrue(validate_metadata(gold))
        self.sample["properties"].pop("sdg_contributions")
        self.assertEqual(validate_metadata(self.sample), [])

    def test_window_inversion_and_vintage_outside_window(self):
        for window in [{"start_year": 2027, "end_year": 2025}, {"start_year": 2020, "end_year": 2025}]:
            self.sample["properties"]["vintage_window"] = window
            self.assertTrue(validate_metadata(self.sample))

    def test_pool_group_and_standard_must_match(self):
        for field, value in [("fungibility_group_id", "forestry_2025-2027_Verra_VCS"), ("standard_category", "CDM"), ("project_type", "COOKSTOVE")]:
            sample = copy.deepcopy(self.sample)
            sample["properties"][field] = value
            self.assertTrue(validate_metadata(sample))
        self.sample["properties"].pop("fungibility_group_id")
        self.assertTrue(validate_metadata(self.sample))
        self.sample["properties"]["is_fungible_pool"] = False
        self.assertEqual(validate_metadata(self.sample), [])

    def test_retirement_amount_and_status_consistency(self):
        self.sample["properties"].update(status="FULLY_RETIRED", retirement_details={
            "retired_amount_tCO2e": 5000, "beneficiary_company": "Demo",
            "retirement_reason": "Offset", "retirement_timestamp": 1794268800,
        })
        self.assertEqual(validate_metadata(self.sample), [])
        self.sample["properties"]["retirement_details"]["retired_amount_tCO2e"] = 5001
        self.assertTrue(validate_metadata(self.sample))


if __name__ == "__main__":
    unittest.main()
