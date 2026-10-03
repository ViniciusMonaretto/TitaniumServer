import pytest

from dataModules.panel import Panel, PressureUnits, SensorTypes


def make_panel_info(**overrides):
    info = {
        "id": 1,
        "name": "Panel",
        "gateway": "gw1",
        "topic": "pressure",
        "color": "#FF0000",
        "group": 1,
        "indicator": "0",
        "sensorType": SensorTypes.Pressure,
        "gain": 2.0,
        "offset": 0.5,
    }
    info.update(overrides)
    return info


class TestPressureUnits:
    """Test the pressure unit whitelist."""

    @pytest.mark.parametrize("unit", ["Pa", "psi", "bar"])
    def test_known_units_are_kept(self, unit):
        assert PressureUnits.GetUnit(unit) == unit

    @pytest.mark.parametrize("unit", [None, "", "kPa", "PSI", "atm"])
    def test_unknown_units_default_to_pa(self, unit):
        assert PressureUnits.GetUnit(unit) == PressureUnits.Pa


class TestPanelPressureRange:
    """Test the zero/max range mapped from the raw gateway values."""

    def test_pressure_panel_reads_range(self):
        panel = Panel(make_panel_info(zeroValue=0, maxValue="10.5"))
        assert panel.zero_value == 0.0
        assert panel.max_value == 10.5
        assert isinstance(panel.zero_value, float)
        assert isinstance(panel.max_value, float)

    def test_pressure_panel_without_range(self):
        panel = Panel(make_panel_info())
        assert panel.zero_value is None
        assert panel.max_value is None

    @pytest.mark.parametrize("zero_value, max_value",
                             [(None, 10), (0, None), (None, None)])
    def test_partial_range_is_dropped(self, zero_value, max_value):
        panel = Panel(make_panel_info(zeroValue=zero_value, maxValue=max_value))
        assert panel.zero_value is None
        assert panel.max_value is None

    def test_non_pressure_panel_ignores_range(self):
        panel = Panel(make_panel_info(
            sensorType=SensorTypes.Temperature, zeroValue=0, maxValue=10))
        assert panel.zero_value is None
        assert panel.max_value is None

    def test_set_range_clears_range(self):
        panel = Panel(make_panel_info(zeroValue=0, maxValue=10))
        panel.set_range(None, None)
        assert panel.zero_value is None
        assert panel.max_value is None


class TestPanelPressureUnit:
    """Test the unit chosen for pressure panels."""

    def test_pressure_panel_reads_unit(self):
        panel = Panel(make_panel_info(pressureUnit="bar"))
        assert panel.pressure_unit == "bar"

    def test_pressure_panel_defaults_to_pa(self):
        assert Panel(make_panel_info()).pressure_unit == PressureUnits.Pa
        assert Panel(make_panel_info(
            pressureUnit="atm")).pressure_unit == PressureUnits.Pa

    def test_non_pressure_panel_has_no_unit(self):
        panel = Panel(make_panel_info(
            sensorType=SensorTypes.Power, pressureUnit="bar"))
        assert panel.pressure_unit is None

    def test_set_pressure_unit_updates_unit(self):
        panel = Panel(make_panel_info())
        panel.set_pressure_unit("psi")
        assert panel.pressure_unit == "psi"


class TestPanelSerialization:
    """Test the range and unit are sent out with the panel."""

    def test_get_calibration_info(self):
        panel = Panel(make_panel_info(
            zeroValue=1, maxValue=5, pressureUnit="psi"))
        assert panel.get_calibration_info() == {
            "gateway": "gw1",
            "indicator": "0",
            "offset": 0.5,
            "gain": 2.0,
            "zeroValue": 1.0,
            "maxValue": 5.0,
            "pressureUnit": "psi"
        }

    def test_get_calibration_info_without_range(self):
        info = Panel(make_panel_info(
            sensorType=SensorTypes.Current)).get_calibration_info()
        assert info["zeroValue"] is None
        assert info["maxValue"] is None
        assert info["pressureUnit"] is None

    def test_to_json_includes_range_and_unit(self):
        panel_json = Panel(make_panel_info(
            zeroValue=0, maxValue=10, pressureUnit="bar")).to_json()
        assert panel_json["zeroValue"] == 0.0
        assert panel_json["maxValue"] == 10.0
        assert panel_json["pressureUnit"] == "bar"

    def test_to_json_round_trip(self):
        panel = Panel(make_panel_info(
            zeroValue=2, maxValue=8, pressureUnit="psi"))
        copy = Panel(panel.to_json())
        assert copy.zero_value == panel.zero_value
        assert copy.max_value == panel.max_value
        assert copy.pressure_unit == panel.pressure_unit
