import { Component, OnInit } from '@angular/core';
import {MatDialog} from '@angular/material/dialog';
import {SensorAddWindowComponent} from '../../components/sensor-add-window/sensor-add-window.component'
import {MainScreenSelector} from "../../services/main-screen-selector.service"
import {MainScreenOptions} from "../../enum/screen-type"
import { UiPanelService } from '../../services/ui-panels.service';

import { CommonModule } from '@angular/common';
import { SideNavOptionComponent } from '../../components/side-nav-option/side-nav-option.component';

@Component({
    selector: 'app-navbar',
    templateUrl: './navbar.component.html',
    styleUrls: ['./navbar.component.scss'],
    imports: [CommonModule, SideNavOptionComponent],
    standalone: true
})
export class NavbarComponent implements OnInit {

  constructor(public dialog: MatDialog, private mainScreenService: MainScreenSelector, private UiPanelsService: UiPanelService) { }

  ngOnInit(): void {
  }

  addNewSensorCallback(sensorData: any): void {
    console.log('Sensor added:', sensorData);
    // Handle the sensor data (e.g., save it to the server)
  }

  addSensor(): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '250px',
      data: {callback: this.addNewSensorCallback.bind(this)}
    });
  }

  getGroupSensorUi()
  {
    let info = Object.keys(this.UiPanelsService.GetUiConfig())
    return info
  }

  setSensor(group: string)
  {
    this.mainScreenService.SelectScreen(MainScreenOptions.SENSORS, group)
  }

  setStatusLOg()
  {
    this.mainScreenService.SelectScreen(MainScreenOptions.STATUS_LOG, null)
  } 

  toogleEdit()
  {
    this.mainScreenService.toogleEdit()
  }

  CanEdit()
  {
    return this.mainScreenService.CanEdit()
  }

}
