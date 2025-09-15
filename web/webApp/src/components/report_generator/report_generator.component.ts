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
import { SensorTreeComponent } from '../sensor-tree/sensor-tree.component';
import { MatRadioModule } from '@angular/material/radio';
import { IoButtonComponent } from '../io-button/io-button.component';

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
    MatDatepickerModule,
    SensorTreeComponent,
    MatRadioModule,
    IoButtonComponent
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

  selectedSensors: { [id: string]: SensorModule } = {}
  selectedGroup: string = ""

  startDate: Date | null = null
  endDate: Date | null = null

  option: string = ""

  timeRangeChoice: string = 'lastHour';

  constructor(public dialogRef: MatDialogRef<ReportGeneratorComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {uiConfig: any[], callback: ((obj: any) => void), canEdit: boolean}
  ) {
    this.uiConfig = {};
    for(let groupIndex in data.uiConfig) {
      var group = data.uiConfig[groupIndex];
      this.uiConfig[group.name] = group.panels;
    }
  }

  ngOnInit(): void {
    this.setTimeRange(this.timeRangeChoice);
  }

  setTimeRange(choice: string) {
    const now = new Date();
    if (choice === 'lastHour') {
      this.endDate = new Date(now);
      this.startDate = new Date(now.getTime() - 60 * 60 * 1000);
    } else if (choice === 'lastDay') {
      this.endDate = new Date(now);
      this.startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    } else if (choice === 'lastWeek') {
      this.endDate = new Date(now);
      this.startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    }
  }

  // Watch for changes to timeRangeChoice
  ngOnChanges(): void {
    if (this.timeRangeChoice !== 'custom') {
      this.setTimeRange(this.timeRangeChoice);
    }
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


  validForm() {
    return Object.keys(this.selectedSensors).length > 0 && this.startDate && this.endDate;
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onApply(): void {
    let selectedPanels = []

    for (let sensor of Object.values(this.selectedSensors)) {
      selectedPanels.push({
        "gateway": sensor.gateway,
        "topic": sensor.topic,
        "indicator": sensor.indicator
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
