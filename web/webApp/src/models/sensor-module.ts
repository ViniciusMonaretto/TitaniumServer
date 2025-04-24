import {SensorTypesEnum} from "../enum/sensor-type"

export class SensorModule{
    public id: number = 0
    public name: string = "";
    public gateway: string = "";
    public topic: string = "";
    public color: string = "#000000"
    public sensorType: SensorTypesEnum = SensorTypesEnum.PREASSURE
    public value: Number|null = null

    constructor(){
        
    }
}