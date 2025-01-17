import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]:Panel} = {}
    subscriptioSensornDic: {[id: string]: Array<SensorModule>} = {}
    tablesInfo: {[key: string]: any[]} = {}

    private selectedSensor: SensorModule|null = null
    
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
        let topicInfo = topic.split('/')
        let tableFullName = this.GetTableName(topicInfo[0], topicInfo[1])
        if( this.tablesInfo[tableFullName])
        {
          this.tablesInfo[tableFullName].push({"value": value, "timestamp":new Date().toISOString()})
          this.tablesInfo[tableFullName] = JSON.parse(JSON.stringify(this.tablesInfo[tableFullName]));
        }
      }
    }

    public OnTableUpdate(data: any)
    {
      this.tablesInfo[data.tableName] = data.info
    }

    GetTableName(gateway:string, table: string)
    {
      return gateway == "*"?table:gateway + '-' + table
    }

    GetTableInfo(gateway:string, table: string)
    {
      let tableFullName = this.GetTableName(gateway, table)
      return this.tablesInfo[tableFullName]
    }

    public setelectSensor(model: SensorModule|null)
    {
      this.selectedSensor = model
    }
  
    public GetSelectedSensor()
    {
      return this.selectedSensor
    }

}
