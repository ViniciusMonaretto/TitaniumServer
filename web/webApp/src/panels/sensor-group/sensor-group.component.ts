import { Component, OnInit } from '@angular/core';
import { UiPanelService } from "../../services/ui-panels.service"
import { SensorModule } from 'src/models/sensor-module';

@Component({
  selector: 'sensor-groups',
  templateUrl: './sensor-group.component.html',
  styleUrls: ['./sensor-group.component.scss']
})
export class SensorGroupComponent implements OnInit {

  constructor(private UiPanelsService: UiPanelService) { }

  ngOnInit(): void {
  }

  getInfoOfGroup(groupName: string)
  {
    let info = this.UiPanelsService.GetUiConfig()[groupName]
    return info
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

}
