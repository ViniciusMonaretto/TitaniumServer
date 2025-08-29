import { Component, OnInit } from '@angular/core';
import { PanelInfo, UiPanelService } from "../../services/ui-panels.service"
import { ServerConectorService } from "../../services/server-conector.service"
import { MatCardModule } from '@angular/material/card';

import { CommonModule } from '@angular/common';
import { GroupOfSensorsComponent } from '../../components/group-of-sensors/group-of-sensors.component';
import { SensorTypesEnum } from '../../enum/sensor-type';
import { SensorModule } from '../../models/sensor-module';
import { MainScreenSelector } from '../../services/main-screen-selector.service';

@Component({
  selector: 'sensor-groups',
  templateUrl: './sensor-group.component.html',
  styleUrls: ['./sensor-group.component.scss'],
  imports: [MatCardModule, CommonModule, GroupOfSensorsComponent],
  standalone: true
})
export class SensorGroupComponent implements OnInit {

  constructor(private UiPanelsService: UiPanelService,
    private mainScreenService: MainScreenSelector,
    private ServerConectorService: ServerConectorService) { }

  ngOnInit(): void {
  }

  getInfoOfGroup() {
    let info = this.UiPanelsService.GetSelectedGroupInfo()
    if (!info) {
      return new PanelInfo()
    }
    return info.panels
  }

  getGroupSelected() {
    return this.UiPanelsService.GetSelectedGroupInfo()?.id
  }

  getGroupName(){
    const groupInfo = this.UiPanelsService.GetSelectedGroupInfo()
    return groupInfo ? groupInfo.name : ''
  }

  getSensorType() {
    return SensorTypesEnum
  }

  getGroupSensorUi() {
    let info = Object.keys(this.UiPanelsService.GetUiConfig())
    return info
  }

  getSensorSelected(): SensorModule | null {
    return this.UiPanelsService.GetSelectedSensor()
  }

  getSelectedSensorTableInfo() {
    let sensor = this.getSensorSelected()
    if (sensor) {
      return this.UiPanelsService.GetCachedSelectedSensorInfo(sensor.topic, sensor.gateway, sensor.indicator)
    }
    return []

  }

  CanEdit() {
    return this.mainScreenService.CanEdit();
  }

  diselectSensor() {
    this.UiPanelsService.setSelectSensor(null)
  }

  loadInfo(tableInfo: any) {
    let info = this.UiPanelsService.GetCachedSelectedSensorInfo(tableInfo['topic'], tableInfo['gateway'], tableInfo['indicator'])
    if (info.length == 0) {
      var endDate = new Date();
      var startDate = new Date()
      startDate.setMinutes(endDate.getMinutes() - 30)
      this.ServerConectorService.sendRequestForTableInfo([{
        "gateway": tableInfo['gateway'],
        "topic": tableInfo['table'],
        "indicator": tableInfo['indicator']
      }],
        this.getGroupName(),
        startDate,
        endDate)
    }
  }

}
