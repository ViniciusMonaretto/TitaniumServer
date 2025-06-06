import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { AlarmModule } from '../models/alarm-module';

@Injectable({
    providedIn: 'root'
})
export class AlarmManagerService {
    private alarms: AlarmModule[] = []
    private events: {[id: number]: Array<any>} = {}
    constructor(private connectorService: ServerConectorService) {
        this.connectorService.setAlarmInfoCallback((data) => {this.alarmInfoCallback(data)})
        this.connectorService.setRemoveAlarmCallback((data) => {this.alarmRemoved(data)})
        this.connectorService.setAddAlarmCallback((data) => {this.alarmAdded(data)})
        this.connectorService.setReceivedEventsCallback((data) => {this.receiveEventsCallback(data["panelId"], data["events"])})
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

    public getEvents(panelId: number)
    {
        if(panelId in this.events)
        {
            return this.events[panelId]
        }
        return null
    }

    private alarmAdded(alarmInfo: AlarmModule)
    {
        this.alarms.push(alarmInfo)
    }

    private receiveEventsCallback(panelId: number, events: Array<any>)
    {
        this.events[panelId] = events
    }
}