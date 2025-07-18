import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { SensorAddWindowComponent } from '../../components/sensor-add-window/sensor-add-window.component'
import { MainScreenSelector } from "../../services/main-screen-selector.service"
import { MainScreenOptions } from "../../enum/screen-type"
import { UiPanelService } from '../../services/ui-panels.service';

import { CommonModule } from '@angular/common';
import { SideNavOptionComponent } from '../../components/side-nav-option/side-nav-option.component';
import { ReportGeneratorComponent } from '../../components/report_generator/report_generator.component';
import { ServerConectorService } from '../../services/server-conector.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
  imports: [CommonModule, SideNavOptionComponent],
  standalone: true
})
export class NavbarComponent implements OnInit {

  constructor(public dialog: MatDialog,
    private mainScreenService: MainScreenSelector,
    private UiPanelsService: UiPanelService,
    private serverConnector: ServerConectorService) { }

  ngOnInit(): void {
  }

  addNewSensorCallback(sensorData: any): void {
    console.log('Sensor added:', sensorData);
    // Handle the sensor data (e.g., save it to the server)
  }

  addSensor(): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '250px',
      data: { callback: this.addNewSensorCallback.bind(this) }
    });
  }

  getGroupSensorUi() {
    let info = Object.keys(this.UiPanelsService.GetUiConfig())
    return info
  }

  setSensor(group: string) {
    this.mainScreenService.SelectScreen(MainScreenOptions.SENSORS, group)
  }

  setStatusLog() {
    this.mainScreenService.SelectScreen(MainScreenOptions.STATUS_LOG, null)
  }

  setAlertScreen() {
    this.mainScreenService.SelectScreen(MainScreenOptions.ALERT_VIEW, null)
  }

  toogleEdit() {
    this.mainScreenService.toogleEdit()
  }

  openReportGenerator() {
    this.dialog.open(ReportGeneratorComponent, {
      width: '550px',
      data: {
        "uiConfig": this.UiPanelsService.GetUiConfig(),
        callback: (reportData: any) => {
          this.requestReport(reportData)
        }
      }
    });
  }

  requestReport(sensorData: any) {
    this.serverConnector.sendRequestForReportInfo(sensorData['selectedSensors'],
      sensorData['group'],
      sensorData['startDate'],
      sensorData['endDate'])
  }

  CanEdit() {
    return this.mainScreenService.CanEdit()
  }

}
