import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { SensorAddWindowComponent } from '../sensor-add-window/sensor-add-window.component';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE, MatNativeDateModule } from '@angular/material/core';
import { BrazilianDateAdapter } from '../../app/brazilian-date-adapter';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';
import { GroupInfo } from '../../services/ui-panels.service';
import { IoButtonComponent } from '../io-button/io-button.component';

export const MY_DATE_FORMATS = {
  parse: {
    dateInput: 'DD/MM/YYYY',
  },
  display: {
    dateInput: 'DD/MM/YYYY',  
    monthYearLabel: 'MMM YYYY',
    dateA11yLabel: 'DD/MM/YYYY',
    monthYearA11yLabel: 'MMMM YYYY',
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
    MatDatepickerModule,
    IoButtonComponent
  ],
  providers: [
    { provide: DateAdapter, useClass: BrazilianDateAdapter },
    { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
    { provide: MAT_DATE_FORMATS, useValue: MY_DATE_FORMATS }
  ],
  standalone: true
})
export class GraphRequestWindowComponent implements OnInit {

  uiConfig: { [id: string]: GroupInfo } = {}

  selectedSensors: Array<SensorModule> = []
  selectedGroup: string = ""

  startDate: Date | null = null
  endDate: Date | null = null

  option: string = ""

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

  getAvailableSensors()
  {
    switch(this.option)
    {
      case "temperature":
        return this.uiConfig[this.selectedGroup].panels.temperature
      case "pressure":
        return this.uiConfig[this.selectedGroup].panels.pressure
      case "power":
        return this.uiConfig[this.selectedGroup].panels.power
      default:
        return []
    }
  }

  validForm() {
    return this.selectedGroup != "" && this.option != "" &&
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
