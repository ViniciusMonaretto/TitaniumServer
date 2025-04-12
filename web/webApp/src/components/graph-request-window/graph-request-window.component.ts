import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SensorAddWindowComponent } from '../sensor-add-window/sensor-add-window.component';
import { SensorModule } from 'src/models/sensor-module';

@Component({
  selector: 'app-graph-request',
  templateUrl: './graph-request-window.component.html',
  styleUrls: ['./graph-request-window.component.scss']
})
export class GraphRequestWindowComponent implements OnInit {

  uiConfig: {[id: string]: any } = {}

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

  getTemperatureSensors()
  {
    return this.uiConfig[this.selectedGroup].temperature
  }

  validForm()
  {
    return this.selectedSensors.length > 0 && 
          ((this.startDate == null && this.endDate == null) ||
          (this.startDate != null && this.endDate == null)  ||
          (this.startDate != null && this.endDate != null && this.startDate?.getTime() < this.endDate.getTime() ))
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  onAddCLick()
  {
    let selectedPanels = []
    for(let panel of this.selectedSensors)
    {
      selectedPanels.push({
        "gateway": panel.gateway,
        "topic": panel.topic
      })
    }

    let obj = {
      "selectedSensors": selectedPanels,
      "startDate": this.startDate,
      "endDate": this.endDate
    }

    this.data.callback(obj)
    this.dialogRef.close();
  }

}
