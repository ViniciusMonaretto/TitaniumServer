import { Injectable } from '@angular/core';
import {GetSensorBaseUnit, GetTableName, SensorModule} from "../models/sensor-module"
import { SensorTypesEnum } from '../enum/sensor-type';
import { GatewayModule } from '../models/gateway-model';
import { DialogHelper } from './dialog-helper.service';
import { MatDialogRef } from '@angular/material/dialog';
import { SpinnerComponent } from '../components/spinner/spinner.component';

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
    subscriptionInfoArrayMap: {[id: string]: {"callback": Function, "tableNames": Array<string>, "groups": Array<string>, "notifyMissing": boolean}} = {}


    gateways: GatewayModule[] = []
    groupSelected: string = ""

    sensorCachedCurrentInfo: {[id: string]: any[]} = {}

    /** Last graph request window range; survives graph panel close/reopen (root service). */
    lastRequestedStartDate: Date | null = null;
    lastRequestedEndDate: Date | null = null;

    /**
     * Last report window, kept apart from the graph one so the two dialogs don't
     * overwrite each other. The choice is stored too: a relative one ("última hora")
     * is recomputed on reopen, only "personalizado" restores the exact dates.
     */
    lastReportStartDate: Date | null = null;
    lastReportEndDate: Date | null = null;
    lastReportTimeRange: string | null = null;

    private selectedSensor: SensorModule|null = null
    private spinnerDialogRef: MatDialogRef<SpinnerComponent> | null = null;
    
    constructor(private dialogHelper: DialogHelper  ) 
    { 
        
    }

    openSpinnerDialog(message: string): void {
      if (this.spinnerDialogRef) {
        this.closeSpinnerDialog();
      } 
      this.spinnerDialogRef = this.dialogHelper.showSpinnerDialog(message, true)
    }
  
    closeSpinnerDialog(): void {
      this.spinnerDialogRef?.close();
      this.spinnerDialogRef = null;
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

    AddGraphRequest(sensorInfos: Array<any>, requestId: any, groups: Array<string>, callback?: Function)
    {
      let arr = []
      for(let sensorInfo of sensorInfos)
      {
        let graphName = GetTableName(sensorInfo["gateway"], sensorInfo["topic"], sensorInfo["indicator"])
        arr.push(graphName)
      }
      if(callback)
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": callback, "tableNames": arr, "groups":groups, "notifyMissing": true}
      }
      else
      {
        this.subscriptionInfoArrayMap[requestId] = {"callback": this.SensorInfoCallback, "tableNames": arr, "groups":groups, "notifyMissing": false}
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

    /**
     * Finds the panel a history table belongs to, across every sensor bucket of the
     * requested groups, and the group it was found in. A graph can mix groups, so the
     * first group holding the table wins.
     */
    FindPanelByTableName(groupIds: Array<string>, tableName: string): {panel: SensorModule, group: GroupInfo} | undefined
    {
      const matchesTable = (x: SensorModule) =>
        GetTableName(x.gateway, x.topic, x.indicator.toString()) == tableName

      for(const groupId of groupIds)
      {
        const group = this.groups[groupId]
        if(!group)
        {
          continue
        }

        const panel = group.panels.temperature.find(matchesTable)
                   ?? group.panels.pressure.find(matchesTable)
                   ?? group.panels.power.find(matchesTable)
        if(panel)
        {
          return {panel: panel, group: group}
        }
      }

      return undefined
    }

    /** Panel name for a history table, with the group when the request spans several. */
    private GetTableDisplayName(groupIds: Array<string>, tableName: string): string
    {
      const found = this.FindPanelByTableName(groupIds, tableName)
      if(!found)
      {
        return tableName
      }
      // Sensors of different groups can share a name, so the group has to show
      return groupIds.length > 1 ? `${found.panel.name} (${found.group.name})` : found.panel.name
    }

    /**
     * A sensor with no reading in the requested range simply never comes back, and the
     * graph would just be missing a line with nothing to say why. Name those sensors.
     */
    private WarnAboutSensorsWithoutData(groupIds: Array<string>, requestedTables: Array<string>, infoArray: any)
    {
      const missing = requestedTables.filter(x => !(x in infoArray))
      if(missing.length == 0)
      {
        return
      }

      const MAX_NAMES = 8
      let names = missing.slice(0, MAX_NAMES).map(x => this.GetTableDisplayName(groupIds, x)).join(", ")
      if(missing.length > MAX_NAMES)
      {
        names += ` e mais ${missing.length - MAX_NAMES}`
      }

      this.dialogHelper.openInfoDialog(
        `Sem dados no período selecionado para: ${names}`, "Sensores sem dados")
    }

    OnStatusInfoUpdate(requestId: any, infoArray:any)
    {
      if(requestId in this.subscriptionInfoArrayMap)
      {
        let obj = this.subscriptionInfoArrayMap[requestId]
        for(let tableName in infoArray)
        {
          let info = {}

          let found = this.FindPanelByTableName(obj.groups, tableName)

          if(found)
          {
            const panel = found.panel
            info = {
              "name": this.GetTableDisplayName(obj.groups, tableName),
              "realName": tableName,
              "color": panel.color,
              "sensorType": panel.sensorType,
              // The graph plots the raw value, without dividing by the multiplier
              "unit": GetSensorBaseUnit(panel.sensorType),
            }
          }
          else
          {
            info = {
              "name": tableName,
              "realName": tableName,
              "color": "#FFFFFF",
              "sensorType": null,
              "unit": "",
            }
          }
          
          obj.callback(info, infoArray[tableName]);
        }

        if(obj.notifyMissing)
        {
          this.WarnAboutSensorsWithoutData(obj.groups, obj.tableNames, infoArray)
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
