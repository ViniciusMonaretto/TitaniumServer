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

  getAlarmData() {
    return {
      "name": this.alarmModule.name,
      "sensor": this.alarmModule.sensor,
      "alarmType": this.alarmModule.alarmType,
      "value": this.alarmModule.value
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
      (this.alarmModule.name != "" && this.alarmModule.sensor != "" && this.alarmModule.value != null)
  }

  onAddCLick(): void {
    this.data.callback(this.getAlarmData())
    this.dialogRef.close();
  }

}
