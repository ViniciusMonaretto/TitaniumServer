import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { AlarmModule } from '../models/alarm-module';

@Injectable({
    providedIn: 'root'
})
export class AlarmManagerService {
    private alarms: AlarmModule[] = []
    private events: {[id: number]: {requestMade: boolean, eventList: Array<any>}} = {}
    constructor(private connectorService: ServerConectorService) {
        this.connectorService.setAlarmInfoCallback((data) => {this.alarmInfoCallback(data)})
        this.connectorService.setRemoveAlarmCallback((data) => {this.alarmRemoved(data)})
        this.connectorService.setAddAlarmCallback((data) => {this.alarmAdded(data)})
        this.connectorService.setReceivedEventsCallback((data, replace) => {this.receiveEventsCallback(data["panelId"], data["events"], replace)})
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

    public isPanelEventsRequested(panelId: number)
    {
        if(panelId in this.events)
        {
            return this.events[panelId].requestMade
        }
        return false
    }

    public getEvents(panelId: number)
    {
        if(panelId in this.events)
        {
            return this.events[panelId].eventList
        }
        return null
    }

    private alarmAdded(alarmInfo: AlarmModule)
    {
        this.alarms.push(alarmInfo)
    }

    private receiveEventsCallback(panelId: number, events: Array<any>, replaceInfo: boolean)
    {
        if(!(panelId in this.events))
        {
            this.events[panelId] = {requestMade: false, eventList: []}
        }

        if(replaceInfo)
        {
            this.events[panelId].eventList = events
            this.events[panelId].requestMade = true
        }
        else
        {
            this.events[panelId].eventList = [...this.events[panelId].eventList, ...events]
        }
    }
}