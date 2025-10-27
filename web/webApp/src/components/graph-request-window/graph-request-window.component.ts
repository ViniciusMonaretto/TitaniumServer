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
import { DialogHelper } from '../../services/dialog-helper.service';

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
  selectedGroup: GroupInfo | null = null

  startDate: Date | null = null
  endDate: Date | null = null

  option: string = ""

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>, private dialogHelper: DialogHelper,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.uiConfig = data.uiConfig
  }

  ngOnInit(): void {
  }

  getGroups(): GroupInfo[] {
    let uiVector = []
    for (let group in this.uiConfig) {
      uiVector.push(this.uiConfig[group])
    }
    return uiVector;
  }

  setTime(event: Event, selectedDateTime: Date | null): void {
    // Early return if no date is selected
    if (!selectedDateTime) {
      console.warn('setTime: No date selected, cannot set time');
      return;
    }

    // Type guard to ensure we have an HTMLInputElement
    const target = event.target as HTMLInputElement;
    if (!target || target.type !== 'time') {
      console.error('setTime: Invalid event target or input type');
      return;
    }

    const timeValue = target.value;

    // Validate time format (HH:MM)
    if (!timeValue || !/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(timeValue)) {
      console.error('setTime: Invalid time format. Expected HH:MM format');
      return;
    }

    try {
      const [hoursStr, minutesStr] = timeValue.split(':');
      const hours = parseInt(hoursStr, 10);
      const minutes = parseInt(minutesStr, 10);

      // Validate parsed values
      if (isNaN(hours) || isNaN(minutes) || hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
        console.error('setTime: Invalid time values. Hours must be 0-23, minutes must be 0-59');
        return;
      }

      // Create a new date object to avoid mutating the original
      const newDate = new Date(selectedDateTime);
      newDate.setHours(hours, minutes, 0, 0); // Reset seconds and milliseconds

      // Update the original date reference
      if (selectedDateTime === this.startDate) {
        this.startDate = newDate;
      } else if (selectedDateTime === this.endDate) {
        this.endDate = newDate;
      }

    } catch (error) {
      console.error('setTime: Error parsing time value:', error);
    }
  }

  getAvailableSensors() {
    if (this.selectedGroup == null) {
      return []
    }
    switch (this.option) {
      case "temperature":
        return this.selectedGroup.panels.temperature
      case "pressure":
        return this.selectedGroup.panels.pressure
      case "power":
        return this.selectedGroup.panels.power
      default:
        return []
    }
  }

  validForm() {
    return this.selectedGroup != null && this.option != "" &&
      ((this.startDate != null && this.endDate == null) ||
        (this.startDate != null && this.endDate != null && this.startDate?.getTime() < this.endDate.getTime()))
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  onAddCLick() {
    let selectedPanels = []

    // Check if date range is greater than 2 weeks
    if (this.startDate != null) {
      const twoWeeksInMs = 14 * 24 * 60 * 60 * 1000; // 14 days in milliseconds
      const endDateToUse = this.endDate || new Date(); // Use current date if endDate is null
      const dateDifference = endDateToUse.getTime() - this.startDate.getTime();
      
      if (dateDifference > twoWeeksInMs) {
        this.dialogHelper.openErrorDialog("O período selecionado não pode ser maior que 2 semanas");
        return;
      }
    }

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
      "group": this.selectedGroup?.id
    }

    this.data.callback(obj)
    this.dialogRef.close();
  }

}
