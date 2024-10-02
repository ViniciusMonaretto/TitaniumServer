import { Component, Inject } from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {SensorTypesEnum} from "../../enum/sensor-type"

@Component({
  selector: 'app-sensor-add-window',
  templateUrl: './sensor-add-window.component.html',
  styleUrls: ['./sensor-add-window.component.scss']
})
export class SensorAddWindowComponent {
  name: string = "";
  gateway: string = "";
  topic: string = "";
  sensorType: SensorTypesEnum = SensorTypesEnum.READ

  public sensorTypes = Object.values(SensorTypesEnum);

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  getSensorData()
  {
    return {
      "name": this.name,
      "gateway": this.gateway,
      "topic": this.topic,
      "sensorType": this.sensorType,
    }
  }

  onAddCLick(): void{
    this.data.callback(this.getSensorData())
    this.dialogRef.close();
  }

}
