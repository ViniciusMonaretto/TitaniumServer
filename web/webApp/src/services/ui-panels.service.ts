import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]:Panel} = {}
    subscriptioMap: {[id: string]: Array<SensorModule | Function>} = {}
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
        let fullTopic = this.GetTableName(sensor.gateway, sensor.topic)
        this.AddSubscription(fullTopic, sensor)
      }
    }

    RemoveGraphSubscription(tableName: string, indexToRemove: number)
    {
      this.subscriptioMap[tableName].splice(indexToRemove, 1);
    }

    AddSubscriptionFromGraph(gateway: string, topic: string, callback: Function)
    {
      let fullTopic = this.GetTableName(gateway, topic)
      return this.AddSubscription(fullTopic, callback)
    } 

    AddSubscription(fullTopic: string, callbackObj: Function | SensorModule)
    {
      if(! (fullTopic in this.subscriptioMap) )
      {
        this.subscriptioMap[fullTopic] = []
      }

      this.subscriptioMap[fullTopic].push(callbackObj)
      if(typeof callbackObj === 'function')
      {
        callbackObj(fullTopic)
      }
      return this.subscriptioMap[fullTopic].length - 1
    }

    OnSubscriptionUpdate(topic: string, value: any)
    {
      let tableFullName = topic
      let topicInfo = []
      if(topic.indexOf('/') != -1)
      {
        topicInfo = topic.split('/')
        
      }
      else
      {
        topicInfo = topic.split('-')
      }
  
      tableFullName = this.GetTableName(topicInfo[0], topicInfo[1])
      
      if(tableFullName in this.subscriptioMap)
      {
        
        if( Array.isArray(value))
        {
          this.tablesInfo[tableFullName] = value
        }
        else
        {
          if( !this.tablesInfo[tableFullName])
          {
            this.tablesInfo[tableFullName] = []
          }
          this.tablesInfo[tableFullName].push({"value": value.data, "timestamp":new Date(value.timestamp).toISOString()})
          this.tablesInfo[tableFullName] = JSON.parse(JSON.stringify(this.tablesInfo[tableFullName]));
        }
        

        for(let callbackObj of this.subscriptioMap[tableFullName])
        {
          if("topic" in callbackObj )
          {
            callbackObj.value = value.data
          }
          else
          {
            callbackObj(tableFullName)
          }
          
        }
      }
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

    GetTableInfoFromTablename(tableFullName: string)
    {
      if(tableFullName in this.tablesInfo)
        return this.tablesInfo[tableFullName]
      return []
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
