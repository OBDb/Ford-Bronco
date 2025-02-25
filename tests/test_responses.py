import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": "2022",
        "signalset": "default.json",
        "tests": [
            ("7E804621E1201", {"BRONCO_GEAR": "1"}),
            ("7E804621E1202", {"BRONCO_GEAR": "2"}),
            ("7E804621E1203", {"BRONCO_GEAR": "3"}),
            ("7E804621E1204", {"BRONCO_GEAR": "4"}),
            ("7E804621E1205", {"BRONCO_GEAR": "5"}),
            ("7E804621E1206", {"BRONCO_GEAR": "6"}),
            ("7E804621E1207", {"BRONCO_GEAR": "7"}),
            ("7E804621E1208", {"BRONCO_GEAR": "8"}),
            ("7E804621E1209", {"BRONCO_GEAR": "9"}),
            ("7E804621E120A", {"BRONCO_GEAR": "10"}),
            ("7E804621E123C", {"BRONCO_GEAR": None}),  # TODO: Meaning unknown, need to test in car
            ("7E804621E1246", {"BRONCO_GEAR": None}),  # TODO: Meaning unknown, need to test in car

            ("7E804621E2364", {"BRONCO_GEAR_SHFT": None}),  # TODO: Meaning unknown, need to test in car
            ("7E804621E2365", {"BRONCO_GEAR_SHFT": None}),  # TODO: Meaning unknown, need to test in car
            ("7E804621E2367", {"BRONCO_GEAR_SHFT": None}),  # TODO: Meaning unknown, need to test in car

            ("7E805621E1CFFFF", {"BRONCO_TOT": -0.0625}),
            ("7E805621E1C000E", {"BRONCO_TOT": 0.875}),
            ("7E805621E1C02A4", {"BRONCO_TOT": 42.25}),

            ("7E80462F42F1A", {"BRONCO_FLI": 10.196078431372548}),
            ("7E80462F42FFE", {"BRONCO_FLI": 99.6078431372549}),
        ]
    },
]

def load_signalset(filename: str) -> str:
    """Load a signalset JSON file from the standard location."""
    signalset_path = REPO_ROOT / "signalsets" / "v3" / filename
    with open(signalset_path) as f:
        return f.read()

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    signalset_json = load_signalset(test_group["signalset"])

    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner(
                signalset_json,
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}, "
                f"Signalset: {test_group['signalset']}): {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
