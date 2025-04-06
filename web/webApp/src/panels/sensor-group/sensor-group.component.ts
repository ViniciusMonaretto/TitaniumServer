import { Component, OnInit } from '@angular/core';
import { UiPanelService } from "../../services/ui-panels.service"
import { ServerConectorService } from "../../services/server-conector.service"

@Component({
  selector: 'sensor-groups',
  templateUrl: './sensor-group.component.html',
  styleUrls: ['./sensor-group.component.scss']
})
export class SensorGroupComponent implements OnInit {

  constructor(private UiPanelsService: UiPanelService, private ServerConectorService: ServerConectorService) { }

  ngOnInit(): void {
  }

  getInfoOfGroup()
  {
    let info = this.UiPanelsService.GetUiConfig()[this.getGroupSelected()]
    return info
  }

  getGroupSelected()
  {
    return this.UiPanelsService.GetGroup()
  }

  getGroupSensorUi()
  {
    let info = Object.keys(this.UiPanelsService.GetUiConfig())
    return info
  }

  getSensorSelected(): any
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
    this.ServerConectorService.sendRequestForTableInfo(tableInfo['gateway'], tableInfo['table'])
  }

}
