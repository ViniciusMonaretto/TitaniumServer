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
import { GroupAddWindowComponent } from '../../components/group-add-window/group-add-window.component';
import { TransitionCheckState } from '@angular/material/checkbox';
import { DialogHelper } from '../../services/dialog-helper.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
  imports: [CommonModule, SideNavOptionComponent],
  standalone: true
})
export class NavbarComponent implements OnInit {

  public panelOptions = MainScreenOptions

  constructor(public dialog: MatDialog,
    private dialogHelper: DialogHelper,
    private mainScreenService: MainScreenSelector,
    private UiPanelsService: UiPanelService,
    private serverConnector: ServerConectorService) { }

 

  ngOnInit(): void {
  }

  addNewSensorCallback(sensorData: any): void {
    console.log('Sensor added:', sensorData);
    // Handle the sensor data (e.g., save it to the server)
  }

  isPanelSelected(panel: number)
  {
    return this.mainScreenService.GetScreen() == panel
  }

  addSensor(): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '250px',
      data: { callback: this.addNewSensorCallback.bind(this) }
    });
  }

  addNewGroup(): void {
    const dialogRef = this.dialog.open(GroupAddWindowComponent, {
      width: '250px',
      data: { callback: (data: any) => {
        this.serverConnector.sendCommand("addGroupPanel", data)
      } }
    });
  }

  deleteGroup(group: number) {
    this.dialogHelper.openQuestionDialog("Deletar Grupo", 
      "Você tem certeza que deseja deletar o grupo?", () => {
        this.serverConnector.sendCommand("removeGroupPanel", {"id": group})
      }
    )
  }

  getGroupSensorUi() {
    var groups = this.UiPanelsService.GetUiConfig()
    return Object.values(groups)
  }

  checkIfGroupIsSelected(group: string)
  {
    return this.UiPanelsService.groupSelected == group
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

  setGatewayScreen() {
    this.mainScreenService.SelectScreen(MainScreenOptions.GATEWAY_VIEW, null)
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
