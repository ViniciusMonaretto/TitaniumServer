import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';
import { Action } from 'rxjs/internal/scheduler/Action';

@Component({
  selector: 'sensor-info-dialog',
  templateUrl: './sensor_info_dialog.component.html',
  styleUrls: ['./sensor_info_dialog.component.scss'],
  imports: [CommonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    MatDialogModule],
  standalone: true
})
export class SensorInfoDialogComponent {

  public sensorName: string = ""
  public gain: number = 0
  public offset: number = 0
  public enableAlarms: boolean = false
  public maxAlarm: number | null | undefined = null
  public minAlarm: number | null | undefined = null

  private panelId = -1
  private gateway = ""
  private topic = ""
  private indicator = 0

  private onApplyAction: ((obj: any) => void)|null = null

  uiConfig: { [id: string]: any } = {}

  constructor(public dialogRef: MatDialogRef<SensorInfoDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {sensorInfo: SensorModule, callback: ((obj: any) => void)}
  ) {
    this.sensorName = data.sensorInfo.name
    this.gain = data.sensorInfo.gain ?? 0
    this.offset = data.sensorInfo.offset ?? 0
    this.panelId =  data.sensorInfo.id
    this.maxAlarm = data.sensorInfo.maxAlarm?.threshold
    this.minAlarm = data.sensorInfo.minAlarm?.threshold

    this.enableAlarms = this.maxAlarm != null || this.minAlarm != null;

    this.gateway = data.sensorInfo.gateway
    this.topic = data.sensorInfo.topic
    this.indicator = data.sensorInfo.indicator
    this.onApplyAction = data.callback;
  }

  validForm() {
    return this.gain != 0 && this.offset != 0 && 
           (!this.enableAlarms || (this.maxAlarm != 0 && this.minAlarm != 0))
  }

  getChangeInfoPanel()
  {
    return {
      "gain": this.gain,
      "offset": this.offset,
      "maxAlarm": this.maxAlarm,
      "minAlarm": this.minAlarm,
      "gateway": this.gateway,
      "topic": this.topic,
      "indicator": this.indicator,
      "panelId": this.panelId
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onApply(): void {
    if (this.onApplyAction)
    {
      this.onApplyAction(this.getChangeInfoPanel())
    }
    this.dialogRef.close();
  }

}
