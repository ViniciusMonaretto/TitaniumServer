import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { AlarmModule } from '../../models/alarm-module';
import { AlarmTypes } from '../../enum/alarm-type';

import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';

import { ColorChromeModule } from 'ngx-color/chrome';
import { GetTableName, SensorModule } from '../../models/sensor-module';



@Component({
  selector: 'app-sensor-add-window',
  templateUrl: './alarm-add-window.component.html',
  styleUrls: ['./alarm-add-window.component.scss'],
  imports: [CommonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    MatDatepickerModule,
    MatDialogModule,
    ColorChromeModule],
  standalone: true
})
export class AlarmAddWindowComponent {

  public selectedGroup = ""
  public option = ""
  public alarmModule: AlarmModule = new AlarmModule()
  public selectedSensor: SensorModule | null = null
  public alarmType = AlarmTypes;
  public alarmKeys = Object.keys(this.alarmType).filter(key => isNaN(Number(key))) as (keyof typeof AlarmTypes)[]

  uiConfig: { [id: string]: any } = {}

  constructor(public dialogRef: MatDialogRef<AlarmAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
      this.uiConfig = data.uiConfig
  }
 
  onNoClick(): void {
    this.dialogRef.close();
  }

  getGroups(): string[] {
    return Object.keys(this.uiConfig);
  }

  getFullTopicName()
  {
    return this.selectedSensor? GetTableName( this.selectedSensor?.gateway, 
      this.selectedSensor?.topic, 
      this.selectedSensor?.indicator.toString()):""
  }

  getAlarmData() {
    return {
      "name": this.alarmModule.name,
      "topic":  this.getFullTopicName(),
      "type": this.alarmModule.alarmType,
      "threshold": this.alarmModule.threshold,
      "panelId":  this.selectedSensor?.id
    }
  }

  getAvailableSensors()
  {
    switch(this.option)
    {
      case "temperature":
        return this.uiConfig[this.selectedGroup].temperature
      case "pressure":
        return this.uiConfig[this.selectedGroup].pressure
      case "power":
        return this.uiConfig[this.selectedGroup].power
      default:
        return []
    }
  }

  validForm() {
    return this.selectedGroup != "" &&
      (this.alarmModule.name != "" && this.getFullTopicName() != "" && this.alarmModule.threshold != null)
  }

  onAddCLick(): void {
    this.data.callback(this.getAlarmData())
    this.dialogRef.close();
  }

}
