import { SensorTypesEnum } from '../enum/sensor-type';
import { GetSensorBaseUnit, GetSensorUnit, PRESSURE_UNITS, SensorModule } from './sensor-module';

describe('SensorModule', () => {
  it('starts without a pressure range or unit', () => {
    const sensor = new SensorModule()
    expect(sensor.zeroValue).toBeNull()
    expect(sensor.maxValue).toBeNull()
    expect(sensor.pressureUnit).toBeNull()
  });

  it('lists the pressure units the server accepts', () => {
    expect([...PRESSURE_UNITS]).toEqual(["Pa", "psi", "bar"])
  });
});

describe('GetSensorBaseUnit', () => {
  it('defaults pressure to Pa', () => {
    expect(GetSensorBaseUnit(SensorTypesEnum.PREASSURE)).toBe("Pa")
    expect(GetSensorBaseUnit(SensorTypesEnum.PREASSURE, null)).toBe("Pa")
  });

  it('uses the chosen pressure unit', () => {
    for (const unit of PRESSURE_UNITS) {
      expect(GetSensorBaseUnit(SensorTypesEnum.PREASSURE, unit)).toBe(unit)
    }
  });

  it('ignores the pressure unit for other sensor types', () => {
    expect(GetSensorBaseUnit(SensorTypesEnum.TEMPERATURE, "bar")).toBe("ºC")
    expect(GetSensorBaseUnit(SensorTypesEnum.POWER, "psi")).toBe("W")
    expect(GetSensorBaseUnit(SensorTypesEnum.STRING, "bar")).toBe("")
  });
});

describe('GetSensorUnit', () => {
  it('prefixes the chosen pressure unit with the multiplier', () => {
    expect(GetSensorUnit(SensorTypesEnum.PREASSURE, 1000)).toBe("kPa")
    expect(GetSensorUnit(SensorTypesEnum.PREASSURE, 1000, "Pa")).toBe("kPa")
    expect(GetSensorUnit(SensorTypesEnum.PREASSURE, 1, "bar")).toBe("bar")
    expect(GetSensorUnit(SensorTypesEnum.PREASSURE, 1, "psi")).toBe("psi")
  });

  it('keeps the old units when no pressure unit is given', () => {
    expect(GetSensorUnit(SensorTypesEnum.PREASSURE)).toBe("Pa")
    expect(GetSensorUnit(SensorTypesEnum.POWER, 1000)).toBe("kW")
    expect(GetSensorUnit(SensorTypesEnum.POWER, 1000, "bar")).toBe("kW")
  });

  it('returns no unit for sensors without one', () => {
    expect(GetSensorUnit(SensorTypesEnum.STRING, 1000, "bar")).toBe("")
  });
});
