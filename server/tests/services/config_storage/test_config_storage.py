import sqlite3
import pytest
from unittest.mock import MagicMock, patch

from services.config_storage.config_storage import ConfigStorage
from dataModules.panel import Panel


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Point ConfigStorage at a throwaway SQLite file."""
    path = str(tmp_path / "test_db.db")
    monkeypatch.setattr(
        "services.config_storage.config_storage.DB_NAME", path)
    return path


@pytest.fixture
def config_storage(db_path):
    with patch('services.config_storage.config_storage.Logger'):
        yield ConfigStorage(MagicMock())


def make_panel(group_id, **overrides):
    info = {
        "name": "Pressure Panel",
        "gateway": "gw1",
        "topic": "pressure",
        "color": "#0000FF",
        "group": group_id,
        "indicator": "0",
        "sensorType": "Pressure",
        "gain": 1.5,
        "offset": 0.25,
        "multiplier": 1,
        "zeroValue": 0,
        "maxValue": 10,
        "pressureUnit": "bar"
    }
    info.update(overrides)
    return Panel(info)


def panel_columns(db_path):
    conn = sqlite3.connect(db_path)
    try:
        return [column[1] for column in conn.execute(
            "PRAGMA table_info(Panels);").fetchall()]
    finally:
        conn.close()


class TestPressureColumns:
    """Test the pressure range/unit columns of the Panels table."""

    def test_new_db_has_pressure_columns(self, config_storage, db_path):
        columns = panel_columns(db_path)
        assert "zeroValue" in columns
        assert "maxValue" in columns
        assert "pressureUnit" in columns

    def test_old_db_is_migrated(self, db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE Panels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gateway TEXT NOT NULL,
                topic TEXT NOT NULL,
                color TEXT NOT NULL,
                panelGroupId INTEGER NOT NULL,
                indicator TEXT NOT NULL,
                sensorType TEXT NOT NULL,
                gain FLOAT,
                offset FLOAT,
                multiplier INTEGER
            );
            """)
        conn.execute("""
            INSERT INTO Panels (name, gateway, topic, color, panelGroupId, indicator, sensorType, gain, offset, multiplier)
            VALUES ('Old', 'gw1', 'pressure', '#000000', 1, '0', 'Pressure', 1, 0, 1)
            """)
        conn.commit()
        conn.close()

        with patch('services.config_storage.config_storage.Logger'):
            storage = ConfigStorage(MagicMock())

        columns = panel_columns(db_path)
        assert "zeroValue" in columns
        assert "maxValue" in columns
        assert "pressureUnit" in columns

        panels = storage.get_panels()
        assert len(panels) == 1
        assert panels[0]["name"] == "Old"
        assert panels[0]["zeroValue"] is None
        assert panels[0]["maxValue"] is None
        assert panels[0]["pressureUnit"] is None

        # A panel loaded from the old row falls back to Pa without a range
        panel = Panel(panels[0])
        assert panel.pressure_unit == "Pa"
        assert panel.zero_value is None
        assert panel.max_value is None

    def test_migration_is_idempotent(self, config_storage, db_path):
        with patch('services.config_storage.config_storage.Logger'):
            ConfigStorage(MagicMock())
        columns = panel_columns(db_path)
        assert columns.count("zeroValue") == 1
        assert columns.count("maxValue") == 1
        assert columns.count("pressureUnit") == 1


class TestPressurePanelStorage:
    """Test the pressure range/unit are saved and loaded."""

    def test_add_panel_saves_range_and_unit(self, config_storage):
        group_id = config_storage.add_panel_group("Group")
        panel_id = config_storage.add_panel(make_panel(group_id))
        assert panel_id > 0

        panels = config_storage.get_panels()
        assert len(panels) == 1
        assert panels[0]["id"] == panel_id
        assert panels[0]["zeroValue"] == 0.0
        assert panels[0]["maxValue"] == 10.0
        assert panels[0]["pressureUnit"] == "bar"

    def test_add_panel_without_range(self, config_storage):
        group_id = config_storage.add_panel_group("Group")
        config_storage.add_panel(make_panel(
            group_id, sensorType="Temperature"))

        panels = config_storage.get_panels()
        assert panels[0]["zeroValue"] is None
        assert panels[0]["maxValue"] is None
        assert panels[0]["pressureUnit"] is None

    def test_update_panel_saves_range_and_unit(self, config_storage):
        group_id = config_storage.add_panel_group("Group")
        panel = make_panel(group_id)
        panel.id = config_storage.add_panel(panel)

        panel.set_range(2.5, 25)
        panel.set_pressure_unit("psi")
        assert config_storage.update_panel(panel)

        saved = config_storage.get_panels()[0]
        assert saved["zeroValue"] == 2.5
        assert saved["maxValue"] == 25.0
        assert saved["pressureUnit"] == "psi"

    def test_update_panel_clears_range(self, config_storage):
        group_id = config_storage.add_panel_group("Group")
        panel = make_panel(group_id)
        panel.id = config_storage.add_panel(panel)

        panel.set_range(None, None)
        assert config_storage.update_panel(panel)

        saved = config_storage.get_panels()[0]
        assert saved["zeroValue"] is None
        assert saved["maxValue"] is None
        assert saved["pressureUnit"] == "bar"

    def test_saved_panel_round_trips_to_panel(self, config_storage):
        group_id = config_storage.add_panel_group("Group")
        original = make_panel(group_id, zeroValue=1, maxValue=4,
                              pressureUnit="psi")
        config_storage.add_panel(original)

        loaded = Panel(config_storage.get_panels()[0])
        assert loaded.get_calibration_info() == original.get_calibration_info()
