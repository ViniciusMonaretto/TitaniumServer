import { SensorTypesEnum } from "../enum/sensor-type"
import { AlarmModule } from "./alarm-module";

export class SensorModule {
    public id: number = 0
    public name: string = "";
    public gateway: string = "";
    public topic: string = "";
    public color: string = "#000000"
    public indicator: number = 0
    public sensorType: SensorTypesEnum = SensorTypesEnum.PREASSURE
    public value: Number | null = null
    public isActive: boolean = false
    public gain: number = 0
    public offset: number = 0
    public maxAlarm: AlarmModule | null = null
    public minAlarm: AlarmModule | null = null
    public multiplier: number = 1
    // Pressure only: values the raw gateway range (600..2400) is mapped to
    public zeroValue: number | null = null
    public maxValue: number | null = null
    // Pressure only: unit the mapped values are in
    public pressureUnit: PressureUnit | null = null

    constructor() {

    }
}

export const PRESSURE_UNITS = ["Pa", "psi", "bar"] as const
export type PressureUnit = typeof PRESSURE_UNITS[number]

export function GetTableName(gateway: string, table: string, indicator: string) {
    return gateway == "*" ? table : gateway + '-' + table + '-' + indicator
}

const SENSOR_BASE_UNITS: { [type: string]: string } = {
    [SensorTypesEnum.PREASSURE]: "Pa",
    [SensorTypesEnum.TEMPERATURE]: "ºC",
    [SensorTypesEnum.POWER]: "W",
    [SensorTypesEnum.CURRENT]: "A",
    [SensorTypesEnum.TENSION]: "V",
    [SensorTypesEnum.POWER_FACTOR]: "%"
}

const MULTIPLIER_PREFIXES: { [multiplier: number]: string } = {
    10: "d",
    100: "c",
    1000: "k"
}

const SENSOR_TYPE_LABELS: { [type: string]: string } = {
    [SensorTypesEnum.PREASSURE]: "Pressão",
    [SensorTypesEnum.TEMPERATURE]: "Temperatura",
    [SensorTypesEnum.POWER]: "Potência",
    [SensorTypesEnum.CURRENT]: "Corrente",
    [SensorTypesEnum.TENSION]: "Tensão",
    [SensorTypesEnum.POWER_FACTOR]: "Fator de Potência",
    [SensorTypesEnum.STRING]: "Texto"
}

/**
 * Factor from the stored value to the base unit. Gateways report pressure in kPa
 * (see IoCloudApiTranslator), but it is shown in Pa.
 */
const STORED_TO_BASE_SCALE: { [type: string]: number } = {
    [SensorTypesEnum.PREASSURE]: 1
}

/** Converts a stored reading (or alarm threshold) to the base unit. */
export function ToBaseUnit(sensorType: SensorTypesEnum | null | undefined, value: number): number {
    return value * (sensorType ? STORED_TO_BASE_SCALE[sensorType] ?? 1 : 1)
}

/** Converts a value typed in the base unit back to how it is stored. */
export function FromBaseUnit(sensorType: SensorTypesEnum | null | undefined, value: number): number {
    return value / (sensorType ? STORED_TO_BASE_SCALE[sensorType] ?? 1 : 1)
}

/**
 * Converts a stored reading to what the panel shows: the base unit divided by the
 * multiplier (e.g. 1500 Pa with multiplier 1000 -> 1.5 kPa). Graphs use this too,
 * so they match the unit returned by GetSensorUnit.
 */
export function ToDisplayUnit(sensorType: SensorTypesEnum | null | undefined, value: number, multiplier: number = 1): number {
    return ToBaseUnit(sensorType, value) / (multiplier || 1)
}

/**
 * Unit of the value converted by ToBaseUnit, ignoring the panel multiplier.
 * Pressure panels choose their own unit, defaulting to Pa.
 */
export function GetSensorBaseUnit(sensorType: SensorTypesEnum, pressureUnit?: PressureUnit | null): string {
    if (sensorType == SensorTypesEnum.PREASSURE && pressureUnit) {
        return pressureUnit
    }
    return SENSOR_BASE_UNITS[sensorType] ?? ""
}

/**
 * Unit shown on the panel, which divides the reading by the multiplier — so the
 * prefix follows that division. e.g. "kW", "ºC", "Pa".
 */
export function GetSensorUnit(sensorType: SensorTypesEnum, multiplier: number = 1, pressureUnit?: PressureUnit | null): string {
    const base = GetSensorBaseUnit(sensorType, pressureUnit)
    if (!base) {
        return base
    }
    return (MULTIPLIER_PREFIXES[multiplier] ?? "") + base
}

/** Display name of a sensor type, as already used by the group screens. */
export function GetSensorTypeLabel(sensorType: SensorTypesEnum): string {
    return SENSOR_TYPE_LABELS[sensorType] ?? String(sensorType)
}
