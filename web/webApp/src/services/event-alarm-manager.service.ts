import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { EventAlarmModule } from '../models/event-alarm-module';

@Injectable({
    providedIn: 'root'
})
export class EventAlarmManagerService {
    private events: Array<EventAlarmModule> = []
    constructor(private connectorService: ServerConectorService) {
        this.connectorService.setReceivedEventsCallback((data, replace) => {this.receiveEventsCallback(data, replace)})
        this.connectorService.addOnConnectCallback(()=>{
            this.connectorService.sendCommand("requestEvents", {})
        })
        
    }

    public removeAllEvents()
    {
        this.connectorService.sendCommand("removeAllEvents", {})
    }

    public getEvents()
    {
        return this.events
    }

    private receiveEventsCallback(events: Array<EventAlarmModule>, replaceInfo: boolean)
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