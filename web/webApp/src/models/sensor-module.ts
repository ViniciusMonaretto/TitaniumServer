import {SensorTypesEnum} from "../enum/sensor-type"
import { AlarmModule } from "./alarm-module";

export class SensorModule{
    public id: number = 0
    public name: string = "";
    public gateway: string = "";
    public topic: string = "";
    public color: string = "#000000"
    public indicator: number = 0
    public sensorType: SensorTypesEnum = SensorTypesEnum.PREASSURE
    public value: Number|null = null
    public isActive: boolean = false
    public gain: number = 0
    public offset: number = 0
    public maxAlarm: AlarmModule | null = null
    public minAlarm: AlarmModule | null = null

    constructor(){
        
    }
}

export function GetTableName(gateway:string, table: string, indicator: string)
{
    return gateway == "*"?table:gateway + '-' + table + '-' + indicator
}