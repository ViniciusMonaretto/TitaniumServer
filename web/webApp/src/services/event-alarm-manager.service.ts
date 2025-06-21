import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { AlarmModule } from '../models/alarm-module';

@Injectable({
    providedIn: 'root'
})
export class EventAlarmManagerService {
    private events: Array<any> = []
    constructor(private connectorService: ServerConectorService) {
        this.connectorService.setReceivedEventsCallback((data, replace) => {this.receiveEventsCallback(data["events"], replace)})
    }

    public requestAllAlarms() {
        this.connectorService.sendCommand("requestEvents", {})
    }

    public removeAlarm(alarmId: number)
    {
        this.connectorService.sendCommand("removeAlarm", alarmId)
    }

    public addAlarm(alarmInfo: AlarmModule)
    {
        this.connectorService.sendCommand("addAlarm", alarmInfo)
    }

    public getEvents()
    {
        return this.events
    }

    private receiveEventsCallback(events: Array<AlarmModule>, replaceInfo: boolean)
    {
        if (replaceInfo)
        {
            this.events = events
        }
        else
        {
            for(var evt of events)
            {
                this.events.push(evt)
            }  
        }
    }
}