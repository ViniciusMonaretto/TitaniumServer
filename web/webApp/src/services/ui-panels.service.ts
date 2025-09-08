import { Injectable } from '@angular/core';
import {GetTableName, SensorModule} from "../models/sensor-module"
import { SensorTypesEnum } from '../enum/sensor-type';
import { table } from 'console';
import { GatewayModule } from '../models/gateway-model';

export class GroupInfo {
  public id: number = -1
  public name: string = ""
  public panels: PanelInfo = new PanelInfo()
}

export class PanelInfo {
  public temperature: Array<SensorModule> = [];
  public pressure: Array<SensorModule>  = [];
  public power: Array<SensorModule> = [];
}

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    groups: {[id: string]:  GroupInfo} = {}
    subscriptioMap: {[id: string]: Array<SensorModule | Function>} = {}
    subscriptionInfoArrayMap: {[id: string]: {"callback": Function, "tableNames": Array<string>, "group": string}} = {}


    gateways: GatewayModule[] = []
    groupSelected: string = ""

    sensorCachedCurrentInfo: {[id: string]: any[]} = {}

    private selectedSensor: SensorModule|null = null
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: any )
    { 
      
      this.RemoveAllSensorModuleSubscription()
      this.groups = {}

      for(let groupId in uiConfig)
      {
        this.groups[groupId] = new GroupInfo()
        this.CreateSensorSubscriptionFromPanel(uiConfig[groupId].panels, groupId)
        if(this.groupSelected == "")
        {
          this.groupSelected = groupId
        }
        
        // Update group info
        this.groups[groupId].name = uiConfig[groupId].groupName
        this.groups[groupId].id = uiConfig[groupId].groupId
      }
    }

    GetPanelById(panelId: number)
    {
      for(var groupPanelsId in this.groups)
      {
        var group = this.groups[groupPanelsId]
        var panel = group.panels.temperature.find(x=>x.id == panelId)
        if (panel)
        {
          return panel
        }
        var panel = group.panels.pressure.find(x=>x.id == panelId)
        if (panel)
        {
          return panel
        }
        var panel = group.panels.power.find(x=>x.id == panelId)
        if (panel)
        {
          return panel
        }
      }
      return null
    }

    GetUiConfig()
    {
      return this.groups
    }

    UpdateGateways(gateways: GatewayModule[])
    {
      this.gateways = gateways
    }
    
    AddSensorToPanel(sensor: SensorModule, groupId: string)
    {
      switch(sensor.sensorType)
      {
        case SensorTypesEnum.TEMPERATURE:
          this.groups[groupId].panels.temperature.push(sensor)
          break
        case SensorTypesEnum.PREASSURE:
          this.groups[groupId].panels.pressure.push(sensor)
          break
        case SensorTypesEnum.TENSION:
        case SensorTypesEnum.CURRENT:
        case SensorTypesEnum.POWER_FACTOR:
        case SensorTypesEnum.POWER:
          this.groups[groupId].panels.power.push(sensor)
          break
      }
    }

    RemoveAllSensorModuleSubscription()
    {
      for(var sensorId in  this.subscriptioMap)
      {
        this.subscriptioMap[sensorId] = this.subscriptioMap[sensorId].filter(x=> !("topic" in x))
      }
    }


    CreateSensorSubscriptionFromPanel(panel: SensorModule[], groupId: string)
    {
      for(var sensor of panel)
      {
        this.AddSensorToPanel(sensor, groupId);
        let fullTopic = GetTableName(sensor.gateway, sensor.topic, sensor.indicator.toString())
        this.AddSubscription(fullTopic, sensor)
      }
    }

    RemoveGraphSubscription(tableName: string, indexToRemove: number)
    {
      this.subscriptioMap[tableName].splice(indexToRemove, 1);
    }

    GetCachedSelectedSensorInfo(topic: string, gateway: string, indicator: number)
    {
      let tableName = GetTableName(gateway, topic, indicator.toString())
      if(tableName in this.sensorCachedCurrentInfo)
      {
        return this.sensorCachedCurrentInfo[tableName]
      }
      return []
    }

    SensorInfoCallback = (info: any, infoArr: any[]) => {
      this.sensorCachedCurrentInfo[info.realName] = infoArr
    }

    AddGraphRequest(sensorInfos: Array<any>, requestId: any, group: string, callback?: Function)
    {
      let arr = []
      for(let sensorInfo of sensorInfos)
      {
        let graphName = GetTableName(sensorInfo["gateway"], sensorInfo["topic"], sensorInfo["indicator"])
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

    GetSelectedGroupInfo()
    {
      return this.groups[this.groupSelected]
    }

    OnStatusInfoUpdate(requestId: any, infoArray:any)
    {
      if(requestId in this.subscriptionInfoArrayMap)
      {
        let obj = this.subscriptionInfoArrayMap[requestId]
        for(let tableName in infoArray)
        {
          let info = {}

          let panel = this.groups[obj.group].panels.temperature.find(x=> GetTableName(x.gateway, 
                                                                               x.topic, 
                                                                               x.indicator.toString()) == tableName)

          if(!panel)
          {
            panel = this.groups[obj.group].panels.pressure.find(x=> GetTableName(x.gateway, 
              x.topic, 
              x.indicator.toString()) == tableName)
          }

          if(!panel)
          {
            panel = this.groups[obj.group].panels.power.find(x=> GetTableName(x.gateway, 
              x.topic, 
              x.indicator.toString()) == tableName)
          }
                                                                               
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

    OnSubscriptionUpdate(topic: string, status_update: any)
    {
      let topicInfo = topic.split('-')
      let tableFullName = GetTableName(topicInfo[0], topicInfo[1], topicInfo[2])
      
      if(tableFullName in this.subscriptioMap)
      {
        for(let callbackObj of this.subscriptioMap[tableFullName])
        {
          if("topic" in callbackObj )
          {
            callbackObj.value = status_update.value
            callbackObj.isActive = status_update.isActive
            if(tableFullName in this.sensorCachedCurrentInfo)
            {
              this.sensorCachedCurrentInfo[tableFullName].push({
                timestamp: status_update["timestamp"],
                value: status_update["data"],
              })
              let filterDate = new Date()
              filterDate.setHours(filterDate.getHours() - 1)
              this.sensorCachedCurrentInfo[tableFullName] = this.sensorCachedCurrentInfo[tableFullName].filter(x=> new Date(x.timestamp) >= filterDate)
            }
          }
          else
          {
            callbackObj(tableFullName, status_update)
          }
          
        }
      }
    }

    public setSelectSensor(model: SensorModule|null)
    {
      this.selectedSensor = model
    }
  
    public GetSelectedSensor(): SensorModule | null
    {
      return this.selectedSensor
    }

}
