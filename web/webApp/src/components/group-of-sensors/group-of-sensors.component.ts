import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from "../../models/sensor-module"
import {MatDialog} from '@angular/material/dialog';
import {SensorAddWindowComponent} from '../../components/sensor-add-window/sensor-add-window.component'

import {ServerConectorService} from "../../services/server-conector.service"
import {UiPanelService} from "../../services/ui-panels.service"

@Component({
  selector: 'group-of-sensors',
  templateUrl: './group-of-sensors.component.html',
  styleUrls: ['./group-of-sensors.component.scss']
})
export class GroupOfSensorsComponent implements OnInit {

  @Input() name: string = "";
  @Input() sensorArray: Array<SensorModule> = [];

  constructor(public dialog: MatDialog, private serverConnector: ServerConectorService, private UiPanelsService: UiPanelService) { }

  ngOnInit(): void {
  }

  addSensor(groupName: string): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '250px',
      data: {callback: (sensorData: any)=>{
        sensorData["group"] = groupName
        this.addNewSensorCallback(sensorData)
      }}
    });
  }

  addNewSensorCallback(sensorData: any): void {
    console.log('Sensor added:', sensorData);
    this.serverConnector.sendCommand("addPanel", sensorData)
  }

  removeSensorCallback(sensorData: any): void {
    console.log('Sensor removed:', sensorData);
    this.serverConnector.sendCommand("removePanel", sensorData)
  }

  selectSensor(sensorInfo: any)
  {
    this.UiPanelsService.setelectSensor(sensorInfo)
  }
}
