import {SensorTypesEnum} from "../enum/sensor-type"

export class SensorModule{
    public id: number = 0
    public name: string = "";
    public gateway: string = "";
    public topic: string = "";
    public sensorType: SensorTypesEnum = SensorTypesEnum.PREASSURE
    public value: Number|null = null

    constructor(){
        
    }
}