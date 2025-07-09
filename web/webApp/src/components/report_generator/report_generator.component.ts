import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';
import { MatNativeDateModule, DateAdapter, NativeDateAdapter, MAT_DATE_LOCALE, MAT_DATE_FORMATS } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MY_DATE_FORMATS } from '../graph-request-window/graph-request-window.component';

@Component({
  selector: 'sensor-info-dialog',
  templateUrl: './report_generator.component.html',
  styleUrls: ['./report_generator.component.scss'],
  imports: [
    CommonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    MatNativeDateModule,
    MatDatepickerModule
  ],
  providers: [
    { provide: DateAdapter, useClass: NativeDateAdapter },
    { provide: MAT_DATE_LOCALE, useValue: 'en-US' },
    { provide: MAT_DATE_FORMATS, useValue: MY_DATE_FORMATS }
  ],
  standalone: true
})
export class ReportGeneratorComponent {
  uiConfig: { [id: string]: any } = {}

  selectedSensors: Array<SensorModule> = []
  selectedGroup: string = ""

  startDate: Date | null = null
  endDate: Date | null = null

  option: string = ""

  constructor(public dialogRef: MatDialogRef<ReportGeneratorComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {uiConfig: { [id: string]: any }, callback: ((obj: any) => void), canEdit: boolean}
  ) {
    this.uiConfig = data.uiConfig
  }

  getGroups(): string[] {
    return Object.keys(this.uiConfig);
  }

  setTime(event: any, selectedDateTime: Date | null) {
    if (selectedDateTime) {
      const [hours, minutes] = event.target.value.split(':');
      selectedDateTime.setHours(parseInt(hours, 10), parseInt(minutes, 10));
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
    return this.selectedSensors.length > 0 && this.startDate && this.endDate;
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onApply(): void {
    let selectedPanels = []
    if (this.selectedSensors.length == 0) {
      this.selectedSensors = this.getAvailableSensors()
    }

    for (let panel of this.selectedSensors) {
      selectedPanels.push({
        "gateway": panel.gateway,
        "topic": panel.topic,
        "indicator": panel.indicator
      })
    }

    let obj = {
      "selectedSensors": selectedPanels,
      "startDate": this.startDate,
      "endDate": this.endDate,
      "group": this.selectedGroup
    }

    this.data.callback(obj)
    this.dialogRef.close();
  }

}
