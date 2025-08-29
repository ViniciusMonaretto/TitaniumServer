import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from "../../models/sensor-module"
import {MatDialog} from '@angular/material/dialog';
import {SensorAddWindowComponent} from '../../components/sensor-add-window/sensor-add-window.component'

import { CommonModule } from '@angular/common';
import { SensorComponent } from '../sensor/sensor.component';

import {ServerConectorService} from "../../services/server-conector.service"
import {UiPanelService} from "../../services/ui-panels.service"
import { SensorTypesEnum } from '../../enum/sensor-type';
import { MatIconModule } from '@angular/material/icon';
import { SensorInfoDialogComponent } from '../sensor_info_dialog/sensor_info_dialog.component';

@Component({
    selector: 'group-of-sensors',
    templateUrl: './group-of-sensors.component.html',
    styleUrls: ['./group-of-sensors.component.scss'],
    imports: [CommonModule, SensorComponent, MatIconModule],
    standalone: true
})
export class GroupOfSensorsComponent implements OnInit {

  @Input() canEdit: boolean = false;
  @Input() name: string = "";
  @Input() group: number = 0;
  @Input() type: string = "";
  @Input() sensorArray: Array<SensorModule> = [];
  @Input() width: string | undefined

  constructor(public dialog: MatDialog, private serverConnector: ServerConectorService) { }

  ngOnInit(): void {
  }

  getStyleOfCell() {
    return this.width ? { width: this.width } : {};
  }

  getGridStyle() {
    const width = this.width || '380px';
    return {
      display: 'grid',
      gridTemplateColumns: `repeat(auto-fill, minmax(${width}, 1fr))`,
      gap: '10px',
      paddingBottom: '10px'
    };
  }

  addSensor(groupId: number): void {
    const dialogRef = this.dialog.open(SensorAddWindowComponent, {
      width: '300px',
      data: {callback: (sensorData: any)=>{
        sensorData["group"] = groupId
        this.addNewSensorCallback(sensorData)
      },
      sensorType: this.type
    }
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

  updatePanelInfo(updatePanelInfo: any)
  {
    this.serverConnector.sendCommand("updatePanelInfo", updatePanelInfo)
  }

  openSensorDialog(sensorInfo: SensorModule)
  {
    const dialogRef = this.dialog.open(SensorInfoDialogComponent, {
      width: '450px',
      data: {sensorInfo: sensorInfo,
      sensorType: this.type,
      canEdit: this.canEdit,
      callback: (calibrateInfo: any) => {
        this.updatePanelInfo(calibrateInfo)
      }
    }
    });
  }
}
