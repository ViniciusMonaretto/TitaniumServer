import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { GetSensorUnit, SensorModule, ToBaseUnit } from '../../models/sensor-module';
import { SensorTypesEnum } from '../../enum/sensor-type';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { throwDialogContentAlreadyAttachedError } from '@angular/cdk/dialog';

@Component({
  selector: 'sensor',
  templateUrl: './sensor.component.html',
  styleUrls: ['./sensor.component.scss'],
  imports: [CommonModule, MatIconModule],
  standalone: true
})
export class SensorComponent implements OnInit {
  @Input() canEdit: boolean = false
  @Input() sensorInfo: SensorModule = new SensorModule()
  @Output() clickCallback: EventEmitter<any> = new EventEmitter();
  @Output() deleteCallback: EventEmitter<any> = new EventEmitter();

  public sensorTypes = Object.values(SensorTypesEnum);

  constructor() { }

  getMeasureIcon(): String {
    return GetSensorUnit(this.sensorInfo.sensorType, this.sensorInfo.multiplier)
  }

  ngOnInit(): void {
    this.sensorInfo.name
  }

  getStatusMessageOfSensor() {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!this.sensorInfo.isActive) {
      return 'Desativado';
    }

    if (!value && value !== 0) {
      return 'sem leitura';
    }

    if (maxValue && value > maxValue) {
      return 'Valor Muito Alto'
    }

    if (minValue && value < minValue) {
      return 'Valor Muito Baixo'
    }

    return 'OK';
  }

  getColorOfReading() {
    return this.sensorInfo.color
  }

  getColorOfSensorStatusMessage() {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!this.sensorInfo.isActive || (!value && value !== 0)) {
      return 'none';
    }

    if (maxValue && value > maxValue) {
      return '#FA3838'
    }

    if (minValue && value < minValue) {
      return 'rgb(31 31 141)'
    }

    return '#22C55E';
  }

  getBackgrounColor()
  {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!this.sensorInfo.isActive || (!value && value !== 0)) {
      return 'none';
    }

    if (maxValue !== null && maxValue !== undefined && value > maxValue) {
      return 'rgb(242 156 156)'
    }

    if (minValue !== null && minValue !== undefined && value < minValue) {
      return 'rgb(196 214 243)'
    }

    return 'none';
  }

  deletePanel() {
    this.deleteCallback.emit(this.sensorInfo.id)
  }

  infoCLick() {
    this.clickCallback.emit(this.sensorInfo)
  }

  getCurrentReading() {
    return this.sensorInfo && this.sensorInfo?.isActive && this.sensorInfo?.value != null ? 
                    (ToBaseUnit(this.sensorInfo.sensorType, Number(this.sensorInfo.value))/this.sensorInfo.multiplier).toFixed(2) : "--"
  }

}
