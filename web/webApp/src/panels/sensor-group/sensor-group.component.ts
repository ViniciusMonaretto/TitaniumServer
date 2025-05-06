import { Component, OnInit } from '@angular/core';
import { PanelInfo, UiPanelService } from "../../services/ui-panels.service"
import { ServerConectorService } from "../../services/server-conector.service"
import { MatCardModule } from '@angular/material/card';

import { CommonModule } from '@angular/common';
import { SensorInfoComponent } from '../../components/sensor-info/sensor-info.component';
import { GroupOfSensorsComponent } from '../../components/group-of-sensors/group-of-sensors.component';
import { SensorTypesEnum } from '../../enum/sensor-type';
import { SensorModule } from '../../models/sensor-module';

@Component({
    selector: 'sensor-groups',
    templateUrl: './sensor-group.component.html',
    styleUrls: ['./sensor-group.component.scss'],
    imports: [MatCardModule, CommonModule, SensorInfoComponent, GroupOfSensorsComponent],
    standalone: true
})
export class SensorGroupComponent implements OnInit {

  constructor(private UiPanelsService: UiPanelService, private ServerConectorService: ServerConectorService) { }

  ngOnInit(): void {
  }

  getInfoOfGroup()
  {
    let info = this.UiPanelsService.GetUiConfig()[this.getGroupSelected()]
    if(!info)
    {
      return new PanelInfo()
    }
    return info
  }

  getGroupSelected()
  {
    return this.UiPanelsService.GetGroup()
  }

  getSensorType()
  {
    return SensorTypesEnum
  }

  getGroupSensorUi()
  {
    let info = Object.keys(this.UiPanelsService.GetUiConfig())
    return info
  }

  getSensorSelected(): SensorModule | null
  {
    return this.UiPanelsService.GetSelectedSensor()
  }

  getSelectedSensorTableInfo()
  {
    let sensor = this.getSensorSelected()
    if(sensor)
    {
      return this.UiPanelsService.GetCachedSelectedSensorInfo(sensor.topic, sensor.gateway)
    }
    return []
    
  }


  diselectSensor()
  {
    this.UiPanelsService.setSelectSensor(null)
  }

  loadInfo(tableInfo:any)
  {
    let info = this.UiPanelsService.GetCachedSelectedSensorInfo(tableInfo['topic'], tableInfo['gateway'])
    if(info.length == 0)
    {
      var endDate = new Date();
      var startDate =  new Date()
      startDate.setMinutes(endDate.getMinutes() - 30)
      this.ServerConectorService.sendRequestForTableInfo([{
                                                          "gateway": tableInfo['gateway'],
                                                          "topic": tableInfo['table']
                                                        }],
                                                         this.getGroupSelected(),
                                                         startDate,
                                                         endDate)
    }
   
  }

}
