import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]: Panel} = {}
    subscriptioMap: {[id: string]: Array<SensorModule | Function>} = {}
    subscriptionInfoArrayMap: {[id: string]: {"callback": Function, "tableNames": Array<string>}} = {}

    groupSelected: string = ""

    sensorCachedCurrentInfo: {[id: string]: any[]} = {}

    private selectedSensor: SensorModule|null = null
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: {[id: string]: Panel} )
    {
        this.panels = uiConfig
        for(let groupName in this.panels)
        {
          this.CreateSensorSubscriptionFromPanel(this.panels[groupName])
          if(this.groupSelected == "")
          {
            this.groupSelected = groupName
          }
        }
        
        
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

    GetCachedSelectedSensorInfo(topic: string, gateway: string)
    {
      let tableName = this.GetTableName(gateway, topic)
      if(tableName in this.sensorCachedCurrentInfo)
      {
        return this.sensorCachedCurrentInfo[tableName]
      }
      return []
    }

    SensorInfoCallback = (tableName: string, infoArr: any[]) => {
      this.sensorCachedCurrentInfo[tableName] = infoArr
    }

    AddGraphRequest(sensorInfos: Array<any>, requestId: any, callback?: Function)
    {
      let arr = []
      for(let sensorInfo of sensorInfos)
      {
        let graphName = this.GetTableName(sensorInfo["gateway"], sensorInfo["topic"])
        arr.push(graphName)
      }
      if(callback)
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": callback, "tableNames": arr}
      }
      else
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": this.SensorInfoCallback, "tableNames": arr}
      }
       
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

    SelectGroup(group: string)
    {
      this.groupSelected = group;
    }

    GetGroup()
    {
      return this.groupSelected
    }

    OnStatusInfoUpdate(requestId: any, infoArray:any)
    {
      if(requestId in this.subscriptionInfoArrayMap)
      {
        let obj = this.subscriptionInfoArrayMap[requestId]
        for(let tableName in infoArray)
        {
          obj.callback(tableName, infoArray[tableName]);
        }

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
            if(tableFullName in this.sensorCachedCurrentInfo)
            {
              this.sensorCachedCurrentInfo[tableFullName].push(value)
              let filterDate = new Date()
              filterDate.setHours(filterDate.getHours() - 1)
              this.sensorCachedCurrentInfo[tableFullName] = this.sensorCachedCurrentInfo[tableFullName].filter(x=> x.timestamp >= filterDate)
            }
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

    public setSelectSensor(model: SensorModule|null)
    {
      this.selectedSensor = model
    }
  
    public GetSelectedSensor()
    {
      return this.selectedSensor
    }

}
