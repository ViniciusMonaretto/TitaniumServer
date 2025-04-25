import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { SensorAddWindowComponent } from '../sensor-add-window/sensor-add-window.component';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE, MatNativeDateModule, NativeDateAdapter } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';

export const MY_DATE_FORMATS = {
  parse: {
    dateInput: 'l, LLL d, yyyy',
  },
  display: {
    dateInput: 'dd/MM/yyyy',   // <- This is the one users will see
    monthYearLabel: 'MMM yyyy',
    dateA11yLabel: 'LL',
    monthYearA11yLabel: 'MMMM yyyy',
  }
};

@Component({
  selector: 'app-graph-request',
  templateUrl: './graph-request-window.component.html',
  styleUrls: ['./graph-request-window.component.scss'],
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
export class GraphRequestWindowComponent implements OnInit {

  uiConfig: { [id: string]: any } = {}

  selectedSensors: Array<SensorModule> = []
  selectedGroup: string = ""

  startDate: Date | null = null
  endDate: Date | null = null

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.uiConfig = data.uiConfig
  }

  ngOnInit(): void {
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

  getTemperatureSensors() {
    return this.uiConfig[this.selectedGroup].temperature
  }

  validForm() {
    return this.selectedGroup != "" &&
      ((this.startDate == null && this.endDate == null) ||
        (this.startDate != null && this.endDate == null) ||
        (this.startDate != null && this.endDate != null && this.startDate?.getTime() < this.endDate.getTime()))
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  onAddCLick() {
    let selectedPanels = []
    if (this.selectedSensors.length == 0) {
      this.selectedSensors = this.getTemperatureSensors()
    }

    for (let panel of this.selectedSensors) {
      selectedPanels.push({
        "gateway": panel.gateway,
        "topic": panel.topic
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
