import {SensorTypesEnum} from "../enum/sensor-type"

export class SensorModule{
    public name: string = "";
    public gateway: string = "";
    public topic: string = "";
    public measure: string = "";
    public sensorType: SensorTypesEnum = SensorTypesEnum.READ

    constructor(){
        
    }
}