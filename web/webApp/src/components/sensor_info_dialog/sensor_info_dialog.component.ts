import { Component, Inject, HostListener, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';
import { ColorChromeModule } from 'ngx-color/chrome';
import { IoButtonComponent } from '../io-button/io-button.component';

@Component({
  selector: 'sensor-info-dialog',
  templateUrl: './sensor_info_dialog.component.html',
  styleUrls: ['./sensor_info_dialog.component.scss'],
  imports: [CommonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    MatDialogModule,
    ColorChromeModule,
    IoButtonComponent],
  standalone: true
})
export class SensorInfoDialogComponent {

  public sensorName: string = ""
  public gain: number = 0
  public offset: number = 0
  public enableAlarms: boolean = false
  public maxAlarm: Number | null | undefined = null
  public minAlarm: Number | null | undefined = null
  public canEdit: boolean = false
  public showPicker: boolean = false
  private panelId = -1
  private gateway = ""
  private topic = ""
  private indicator = 0
  color: string = ""
  newName: string = ""  
  kiloSelected: boolean = false

  private onApplyAction: ((obj: any) => void) | null = null

  uiConfig: { [id: string]: any } = {}
  calibrate: boolean = false

  constructor(public dialogRef: MatDialogRef<SensorInfoDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { sensorInfo: SensorModule, callback: ((obj: any) => void), canEdit: boolean },
    private elementRef: ElementRef
  ) {
    this.sensorName = data.sensorInfo.name
    this.newName = this.sensorName
    this.gain = data.sensorInfo.gain ?? null
    this.offset = data.sensorInfo.offset ?? null
    this.panelId = data.sensorInfo.id
    this.maxAlarm = data.sensorInfo.maxAlarm?.threshold
    this.minAlarm = data.sensorInfo.minAlarm?.threshold

    this.calibrate = this.gain != null && this.offset != null

    this.enableAlarms = this.maxAlarm != null || this.minAlarm != null;

    this.gateway = data.sensorInfo.gateway
    this.topic = data.sensorInfo.topic
    this.indicator = data.sensorInfo.indicator
    this.onApplyAction = data.callback;
    this.canEdit = data.canEdit
    this.color = data.sensorInfo.color
    this.kiloSelected = data.sensorInfo.multiplier == 1000
  }

  validForm() {
    var choosenMultiplier = this.kiloSelected ? 1000 : 1
    var validMultiplier = choosenMultiplier != this.data.sensorInfo.multiplier
    var isColorDifferent = this.color !== this.data.sensorInfo.color
    var isNameDifferent = this.newName !== this.data.sensorInfo.name
    var validCalibration = !this.calibrate ||   
                           (this.gain !== null && this.offset !== null)
    console.log(validCalibration)
    return this.canEdit && (this.calibrate || this.enableAlarms || isColorDifferent || isNameDifferent || validMultiplier) && (validCalibration)
  }

  getChangeInfoPanel() {
    return {
      "name": this.newName,
      "gain": this.gain,
      "offset": this.offset,
      "maxAlarm": this.maxAlarm,
      "minAlarm": this.minAlarm,
      "gateway": this.gateway,
      "topic": this.topic,
      "indicator": this.indicator,
      "panelId": this.panelId,
      "color": this.color,
      "multiplier": this.kiloSelected ? 1000 : 1
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onApply(): void {
    if (this.onApplyAction) {
      this.onApplyAction(this.getChangeInfoPanel())
    }
    this.dialogRef.close();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    if (this.showPicker) {
      const clickedElement = event.target as HTMLElement;
      const colorPickerElement = this.elementRef.nativeElement.querySelector('color-chrome');
      const inputElement = this.elementRef.nativeElement.querySelector('input[readonly]');
      
      // Check if click is outside both the color picker and the input field
      if (colorPickerElement && !colorPickerElement.contains(clickedElement) && 
          inputElement && !inputElement.contains(clickedElement)) {
        this.showPicker = false;
      }
    }
  }

}
