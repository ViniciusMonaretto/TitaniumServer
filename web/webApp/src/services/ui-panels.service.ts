import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]:Panel} = {}
    subscriptioSensornDic: {[id: string]: Array<SensorModule>} = {}
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: {'panels': Panel} )
    {
        this.panels["base"] = uiConfig['panels']
        this.CreateSensorSubscriptionFromPanel(this.panels["base"])
    }

    GetUiConfig()
    {
      return this.panels
    }

    CreateSensorSubscriptionFromPanel(panel: Panel)
    {
      for(var sensor of panel)
      {
        let fullTopic = sensor.gateway + '/' + sensor.topic
        if(! (fullTopic in this.subscriptioSensornDic) )
        {
          this.subscriptioSensornDic[fullTopic] = []
        }

        this.subscriptioSensornDic[fullTopic].push(sensor)
      }
    }

    OnSubscriptionUpdate(topic: string, value: number)
    {
      if(topic in this.subscriptioSensornDic)
      {
        for(let sensor of this.subscriptioSensornDic[topic])
        {
          sensor.value = value
        }
      }
    }

}
