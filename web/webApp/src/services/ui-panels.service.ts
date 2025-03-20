import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]: Panel} = {}
    subscriptioMap: {[id: string]: Array<SensorModule | Function>} = {}
    subscriptionInfoArrayMap: {[id: string]: {"callback": Function, "tableName": string}} = {}

    private selectedSensor: SensorModule|null = null
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: Panel )
    {
        this.panels["base"] = uiConfig
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

    AddGraphRequest(gateway: string, topic: string, requestId: any, callback: Function)
    {
      this.subscriptionInfoArrayMap[requestId] = {"callback": callback, "tableName": this.GetTableName(gateway,topic)}
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

    OnStatusInfoUpdate(requestId: any, infoArray:any)
    {
      if(requestId in this.subscriptionInfoArrayMap)
      {
        let obj = this.subscriptionInfoArrayMap[requestId]
        obj.callback(obj.tableName, infoArray);

        delete this.subscriptionInfoArrayMap[requestId]
      }
    }

    OnSubscriptionUpdate(topic: string, value: any)
    {
      let topicInfo = topic.split('/')
      let tableFullName = this.GetTableName(topicInfo[0], topicInfo[1])
      
      if(tableFullName in this.subscriptioMap)
      {
        for(let callbackObj of this.subscriptioMap[tableFullName])
        {
          if("topic" in callbackObj )
          {
            callbackObj.value = value.data
          }
          else
          {
            callbackObj(tableFullName, value)
          }
          
        }
      }
    }

    GetTableName(gateway:string, table: string)
    {
      return gateway == "*"?table:gateway + '-' + table
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
