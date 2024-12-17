import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from "../../models/sensor-module"
import {MatDialog} from '@angular/material/dialog';
import {SensorAddWindowComponent} from '../../components/sensor-add-window/sensor-add-window.component'

import {ServerConectorService} from "../../services/server-conector.service"

@Component({
  selector: 'group-of-sensors',
  templateUrl: './group-of-sensors.component.html',
  styleUrls: ['./group-of-sensors.component.scss']
})
export class GroupOfSensorsComponent implements OnInit {

  @Input() name: string = "";
  @Input() sensorArray: Array<SensorModule> = [];

  constructor(public dialog: MatDialog, private serverConnector: ServerConectorService) { }

  ngOnInit(): void {
  }

  addSensor(): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '250px',
      data: {callback: this.addNewSensorCallback.bind(this)}
    });
  }

  addNewSensorCallback(sensorData: any): void {
    console.log('Sensor added:', sensorData);
    this.serverConnector.sendCommand("addPanel", sensorData)
  }
}
