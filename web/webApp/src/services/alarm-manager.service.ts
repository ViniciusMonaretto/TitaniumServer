import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { AlarmModule } from '../models/alarm-module';

@Injectable({
    providedIn: 'root'
})
export class AlarmManagerService {
    private alarms: AlarmModule[] = []
    constructor(private connectorService: ServerConectorService) {
        this.connectorService.setAlarmInfoCallback((data) => {this.alarmInfoCallback(data)})
        this.connectorService.setRemoveAlarmCallback((data) => {this.alarmRemoved(data)})
        this.connectorService.setAddAlarmCallback((data) => {this.alarmAdded(data)})
    }

    private alarmInfoCallback(alarms: any){
        this.alarms = alarms;
    }

    public getAlarms()
    {
        return this.alarms
    }

    public requestAllAlarms() {
        this.connectorService.sendCommand("requestAlarms", {})
    }

    public removeAlarm(alarmId: number)
    {
        this.connectorService.sendCommand("removeAlarm", alarmId)
    }

    private alarmRemoved(alarmId: number)
    {
        this.alarms = this.alarms.filter(item => item.id !== alarmId);
    }

    public addAlarm(alarmInfo: AlarmModule)
    {
        this.connectorService.sendCommand("addAlarm", alarmInfo)
    }

    private alarmAdded(alarmInfo: AlarmModule)
    {
        this.alarms.push(alarmInfo)
    }
}