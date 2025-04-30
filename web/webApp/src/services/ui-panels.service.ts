import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
import { SensorTypesEnum } from '../enum/sensor-type';
import { table } from 'console';

export class PanelInfo {
  public temperature: Array<SensorModule> = [];
  public pressure: Array<SensorModule>  = [];
  public power: Array<SensorModule> = [];
}

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]:  PanelInfo} = {}
    subscriptioMap: {[id: string]: Array<SensorModule | Function>} = {}
    subscriptionInfoArrayMap: {[id: string]: {"callback": Function, "tableNames": Array<string>, "group": string}} = {}

    groupSelected: string = ""

    sensorCachedCurrentInfo: {[id: string]: any[]} = {}

    private selectedSensor: SensorModule|null = null
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: {[id: string]: SensorModule[]} )
    {
        for(let groupName in uiConfig)
        {
          this.panels[groupName] = new PanelInfo()
          this.CreateSensorSubscriptionFromPanel(uiConfig[groupName], groupName)
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

    AddSensorToPanel(sensor: SensorModule, groupName: string)
    {
      switch(sensor.sensorType)
      {
        case SensorTypesEnum.TEMPERATURE:
          this.panels[groupName].temperature.push(sensor)
          break
        case SensorTypesEnum.PREASSURE:
          this.panels[groupName]["pressure"].push(sensor)
          break
        case SensorTypesEnum.POWER:
          this.panels[groupName]["power"].push(sensor)
          break
      }
    }

    CreateSensorSubscriptionFromPanel(panel: SensorModule[], groupName: string)
    {
      for(var sensor of panel)
      {
        this.AddSensorToPanel(sensor, groupName);
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

    AddGraphRequest(sensorInfos: Array<any>, requestId: any, group: string, callback?: Function)
    {
      let arr = []
      for(let sensorInfo of sensorInfos)
      {
        let graphName = this.GetTableName(sensorInfo["gateway"], sensorInfo["topic"])
        arr.push(graphName)
      }
      if(callback)
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": callback, "tableNames": arr, "group":group}
      }
      else
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": this.SensorInfoCallback, "tableNames": arr, "group":group}
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
          let info = {}

          let panel = this.panels[obj.group].temperature.find(x=> this.GetTableName(x.gateway, x.topic) == tableName)
          if(panel)
          {
            info = {
              "name": panel?.name,
              "realName": tableName,
              "color": panel?.color,
            }
          }
          else
          {
            info = {
              "name": tableName,
              "realName": tableName,
              "color": "#FFFFFF",
            }
          }
          
          obj.callback(info, infoArray[tableName]);
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
