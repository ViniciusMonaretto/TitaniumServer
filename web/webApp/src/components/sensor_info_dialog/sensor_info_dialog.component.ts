import { Component, Inject, HostListener, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { FromBaseUnit, GetSensorBaseUnit, PRESSURE_UNITS, PressureUnit, SensorModule, ToBaseUnit } from '../../models/sensor-module';
import { SensorTypesEnum } from '../../enum/sensor-type';
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
  isPressure: boolean = false
  enableRange: boolean = false
  zeroValue: Number | null | undefined = null
  maxValue: Number | null | undefined = null
  pressureUnits = PRESSURE_UNITS
  pressureUnit: PressureUnit = "Pa"

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
    // Thresholds are stored like the readings, but typed in the unit the panel shows
    this.maxAlarm = this.thresholdToBaseUnit(data.sensorInfo.maxAlarm?.threshold)
    this.minAlarm = this.thresholdToBaseUnit(data.sensorInfo.minAlarm?.threshold)

    this.calibrate = this.gain != null && this.offset != null

    this.enableAlarms = this.maxAlarm != null || this.minAlarm != null;

    this.gateway = data.sensorInfo.gateway
    this.topic = data.sensorInfo.topic
    this.indicator = data.sensorInfo.indicator
    this.onApplyAction = data.callback;
    this.canEdit = data.canEdit
    this.color = data.sensorInfo.color
    this.kiloSelected = data.sensorInfo.multiplier == 1000

    this.isPressure = data.sensorInfo.sensorType == SensorTypesEnum.PREASSURE
    this.pressureUnit = data.sensorInfo.pressureUnit ?? "Pa"
    this.zeroValue = this.thresholdToBaseUnit(data.sensorInfo.zeroValue)
    this.maxValue = this.thresholdToBaseUnit(data.sensorInfo.maxValue)
    this.enableRange = this.isPressure && this.zeroValue != null && this.maxValue != null
  }

  get baseUnit(): string {
    return GetSensorBaseUnit(this.data.sensorInfo.sensorType, this.isPressure ? this.pressureUnit : null)
  }

  /** Only Pa has a kilo prefix worth showing (kPa); psi and bar are shown as they are. */
  canUseKilo(): boolean {
    return !this.isPressure || this.pressureUnit == "Pa"
  }

  private getMultiplier(): number {
    return this.kiloSelected && this.canUseKilo() ? 1000 : 1
  }

  isPressureUnitDifferent() {
    return this.isPressure && this.pressureUnit != (this.data.sensorInfo.pressureUnit ?? "Pa")
  }

  validRange() {
    return !this.enableRange ||
           (this.zeroValue != null && this.maxValue != null && Number(this.maxValue) > Number(this.zeroValue))
  }

  isRangeDifferent() {
    var range = this.getRange()
    return range.zeroValue != (this.data.sensorInfo.zeroValue ?? null) ||
           range.maxValue != (this.data.sensorInfo.maxValue ?? null)
  }

  private getRange() {
    var useRange = this.isPressure && this.enableRange
    return {
      zeroValue: useRange ? this.thresholdFromBaseUnit(this.zeroValue) ?? null : null,
      maxValue: useRange ? this.thresholdFromBaseUnit(this.maxValue) ?? null : null
    }
  }

  validForm() {
    var choosenMultiplier = this.getMultiplier()
    var validMultiplier = choosenMultiplier != this.data.sensorInfo.multiplier
    var isColorDifferent = this.color !== this.data.sensorInfo.color
    var isNameDifferent = this.newName !== this.data.sensorInfo.name
    var validCalibration = !this.calibrate ||   
                           (this.gain !== null && this.offset !== null)
    console.log(validCalibration)
    return this.canEdit && (this.calibrate || this.enableAlarms || isColorDifferent || isNameDifferent || validMultiplier || this.isRangeDifferent() || this.isPressureUnitDifferent()) &&
           validCalibration && this.validRange()
  }

  getChangeInfoPanel() {
    return {
      "name": this.newName,
      "gain": this.gain,
      "offset": this.offset,
      "maxAlarm": this.enableAlarms ? this.thresholdFromBaseUnit(this.maxAlarm) : null,
      "minAlarm": this.enableAlarms ? this.thresholdFromBaseUnit(this.minAlarm) : null,
      "gateway": this.gateway,
      "topic": this.topic,
      "indicator": this.indicator,
      "panelId": this.panelId,
      "color": this.color,
      "multiplier": this.getMultiplier(),
      "pressureUnit": this.isPressure ? this.pressureUnit : null,
      ...this.getRange()
    }
  }

  private thresholdToBaseUnit(threshold: Number | null | undefined): Number | null | undefined {
    if (threshold == null) {
      return threshold
    }
    // Drop float noise from the scaling, e.g. 101.45 kPa -> 101449.99999999999 Pa
    return Number(ToBaseUnit(this.data.sensorInfo.sensorType, Number(threshold)).toPrecision(12))
  }

  private thresholdFromBaseUnit(threshold: Number | null | undefined): Number | null | undefined {
    return threshold == null ? threshold : FromBaseUnit(this.data.sensorInfo.sensorType, Number(threshold))
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
