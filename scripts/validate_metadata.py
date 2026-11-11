"""Validate CarbonChain metadata, including rules JSON Schema cannot express."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs/METADATA_SCHEMA.json"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def validate_metadata(metadata: dict) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = [f"{'/'.join(map(str, error.absolute_path)) or '/'}: {error.message}"
              for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(metadata)]
    if errors:
        return errors
    p = metadata["properties"]
    window = p["vintage_window"]
    if not window["start_year"] <= p["vintage_year"] <= window["end_year"]:
        errors.append("vintage_window: require start_year <= vintage_year <= end_year")
    expected_group = f"{p['asset_class']}_{window['start_year']}-{window['end_year']}_{p['standard_category']}"
    if "fungibility_group_id" in p and p["fungibility_group_id"] != expected_group:
        errors.append(f"fungibility_group_id: expected {expected_group}")
    if "fungibility_pool_id" in p:
        errors.append("fungibility_pool_id is retired; use fungibility_group_id")
    categories = {
        "Verra VCS": "Verra_VCS", "Verra VCS + CCB": "Verra_VCS",
        "Verra VCS + SD VISta": "Verra_VCS", "Gold Standard VER": "Gold_Standard",
        "Gold Standard CER": "Gold_Standard", "CDM": "CDM",
        "Vietnam VCM": "Vietnam_VCM", "Article 6.4": "Article_6_4",
    }
    if p["standard_category"] != categories[p["standard"]]:
        errors.append("standard_category does not match standard")
    asset_classes = {"FORESTRY_AFOLU": "forestry", "RENEWABLE_ENERGY": "renewable_energy",
                     "WASTE_MANAGEMENT": "waste_treatment", "ENERGY_EFFICIENCY": "energy_efficiency",
                     "COOKSTOVE": "cookstove", "BLUE_CARBON": "blue_carbon", "AGRICULTURE": "agriculture",
                     "TRANSPORT": "transport", "INDUSTRIAL_GAS": "industrial_gas", "OTHER": "other"}
    if "project_type" in p and p["asset_class"] != asset_classes[p["project_type"]]:
        errors.append("asset_class does not match project_type")
    basis_points = Decimal(str(p["permanence_risk_buffer"])) * 100
    if basis_points != basis_points.to_integral_value():
        errors.append("permanence_risk_buffer must be representable in whole basis points")
    retired = p.get("retirement_details", {}).get("retired_amount_tCO2e", 0)
    issued = p["total_issued_tCO2e"]
    if retired > issued:
        errors.append("retired_amount_tCO2e exceeds total_issued_tCO2e")
    if p["status"] == "FULLY_RETIRED" and retired != issued:
        errors.append("FULLY_RETIRED requires retired amount == total issued")
    if p["status"] == "PARTIALLY_RETIRED" and not 0 < retired < issued:
        errors.append("PARTIALLY_RETIRED requires 0 < retired amount < total issued")
    sdgs = [item["sdg_number"] for item in p.get("sdg_contributions", [])]
    if len(set(sdgs)) != len(sdgs):
        errors.append("sdg_contributions contains duplicate SDG numbers")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args()
    schema = load_json(SCHEMA_PATH)
    samples = [(name, value["const"]) for name, value in schema["$defs"].items() if "const" in value]
    samples += [(str(path), load_json(path)) for path in args.files]
    failed = False
    for name, sample in samples:
        errors = validate_metadata(sample)
        print(f"{'FAIL' if errors else 'PASS'} {name}")
        for error in errors:
            print(f"  {error}")
        failed |= bool(errors)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
