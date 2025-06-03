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
    }

    private alarmInfoCallback(alarms: any){
        this.alarms = JSON.parse(JSON.stringify(alarms["data"]));
    }

    public getAlarms()
    {
        return this.alarms
    }

    public requestAllAlarms() {
        this.connectorService.sendCommand("requestAlarms", {})
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