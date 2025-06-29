import { SensorTypesEnum } from "../enum/sensor-type";
import { SensorModule } from "./sensor-module";

export class EventAlarmModule{
    public id: number = 0
    public alarmId: string = "";
    public panelId: number = 0;
    public timestamp: Date|null = null
    public value: Number = 0
    public name: string = ""

    public panelName: string = ""
    public panelType: SensorTypesEnum = SensorTypesEnum.PREASSURE

    constructor(){
        
    }

    public setPanel(panel: SensorModule | null)
    {
        if (panel)
        {
            this.panelName = panel.name
            this.panelType = panel.sensorType
        }
    }
}