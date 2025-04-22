import { Component, Inject } from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef, MatDialogModule} from '@angular/material/dialog';
import {SensorTypesEnum} from "../../enum/sensor-type"
import {SensorModule} from "../../models/sensor-module"

import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';


@Component({
    selector: 'app-sensor-add-window',
    templateUrl: './sensor-add-window.component.html',
    styleUrls: ['./sensor-add-window.component.scss'],
    imports: [CommonModule,
        MatFormFieldModule,
        MatSelectModule,
        MatInputModule,
        FormsModule,
        MatDatepickerModule,
        MatDialogModule],
    standalone: true
})
export class SensorAddWindowComponent {
  public sensorModule: SensorModule = new SensorModule()

  public sensorTypes = Object.values(SensorTypesEnum);

  settedType?: SensorTypesEnum
  group: string = ""

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.settedType = data.sensorType
    this.group = data.group
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  getSensorData()
  {
    if(this.settedType != undefined)
      this.sensorModule.sensorType = this.settedType
    return {
      "name": this.sensorModule.name,
      "gateway": this.sensorModule.gateway,
      "topic": this.sensorModule.topic,
      "sensorType": this.sensorModule.sensorType,
      "group": this.group
    }
  }

  validForm()
  {
    return this.sensorModule.name != "" &&
           this.sensorModule.gateway != "" &&
           this.sensorModule.topic != "" 
  }

  onAddCLick(): void{
    this.data.callback(this.getSensorData())
    this.dialogRef.close();
  }

}
