import { Component, OnInit } from '@angular/core';
import { UiPanelService } from "../../services/ui-panels.service"

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
    return this.UiPanelsService.GetUiConfig()[groupName]
  }

  getGroupSensorUi()
  {
    return Object.keys(this.UiPanelsService.GetUiConfig())
  }

}
