import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { SensorModule } from '../../models/sensor-module';
import { DateAdapter, MAT_DATE_LOCALE, MAT_DATE_FORMATS, MatNativeDateModule } from '@angular/material/core';
import { BrazilianDateAdapter } from '../../app/brazilian-date-adapter';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MY_DATE_FORMATS } from '../graph-request-window/graph-request-window.component';
import { SensorSelectorComponent } from '../sensor-selector/sensor-selector.component';
import { GroupInfo } from '../../services/ui-panels.service';
import { MatRadioModule } from '@angular/material/radio';
import { IoButtonComponent } from '../io-button/io-button.component';
import { DialogHelper } from '../../services/dialog-helper.service';

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
    SensorSelectorComponent,
    MatRadioModule,
    IoButtonComponent
  ],
  providers: [
    { provide: DateAdapter, useClass: BrazilianDateAdapter },
    { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
    { provide: MAT_DATE_FORMATS, useValue: MY_DATE_FORMATS }
  ],
  standalone: true
})
export class ReportGeneratorComponent {
  uiConfig: { [id: string]: GroupInfo } = {}

  selectedSensors: Array<SensorModule> = []
  selectedGroups: Array<GroupInfo> = []

  startDate: Date | null = null
  endDate: Date | null = null

  option: string = ""

  timeRangeChoice: string = 'lastHour';

  constructor(public dialogRef: MatDialogRef<ReportGeneratorComponent>, public dialogHelper: DialogHelper,
    @Inject(MAT_DIALOG_DATA) public data: {uiConfig: { [id: string]: GroupInfo }, callback: ((obj: any) => void),
      canEdit: boolean, timeRange?: string | null, startDate?: Date | null, endDate?: Date | null}
  ) {
    this.uiConfig = data.uiConfig
    this.timeRangeChoice = data.timeRange ?? this.timeRangeChoice
    this.startDate = data.startDate ?? null
    this.endDate = data.endDate ?? null
  }

  ngOnInit(): void {
    // A relative range means "the last hour from now", so only a custom one keeps
    // the dates it was reopened with
    if (this.timeRangeChoice !== 'custom' || this.startDate == null || this.endDate == null) {
      this.setTimeRange(this.timeRangeChoice);
    }
  }

  /** Formats a Date as HH:mm for native <input type="time"> */
  timeInputValue(date: Date | null): string {
    if (!date) {
      return '';
    }
    const h = date.getHours().toString().padStart(2, '0');
    const m = date.getMinutes().toString().padStart(2, '0');
    return `${h}:${m}`;
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

  setTime(event: any, selectedDateTime: Date | null) {
    if (selectedDateTime) {
      const [hours, minutes] = event.target.value.split(':');
      selectedDateTime.setHours(parseInt(hours, 10), parseInt(minutes, 10));
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


    for (let sensor of this.selectedSensors) {
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
      "groups": this.selectedGroups.map(x => String(x.id)),
      "timeRange": this.timeRangeChoice
    }

    this.data.callback(obj)
    this.dialogRef.close();
  }

}
