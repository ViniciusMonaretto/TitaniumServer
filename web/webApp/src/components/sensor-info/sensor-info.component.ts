import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';

import { SensorModule } from '../../models/sensor-module';
import { GraphComponent } from '../graph/graph.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { IoCloudTableComponent } from '../io-cloud-table/io-cloud-table.component';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'sensor-info',
  templateUrl: './sensor-info.component.html',
  styleUrls: ['./sensor-info.component.scss'],
  imports: [MatCardModule,
    CommonModule,
    GraphComponent,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    IoCloudTableComponent,
    FormsModule,
    MatIconModule], // Add MatCardModule to imports
  standalone: true
})
export class SensorInfoComponent implements OnInit {

  @Input() sensorInfo: SensorModule | null = new SensorModule()
  @Input() currentReading: any = ""
  @Input() set sensorData(data: any[]) {
    this.setLineData(data)
  }
  @Input() events: Array<any> = []
  @Input() enableEdit: boolean = false

  @Output() onLoad: EventEmitter<any> = new EventEmitter()
  @Output() onExit: EventEmitter<any> = new EventEmitter()

  resizeTrigger: boolean = false

  headerInfo: string[][] = [["name", "Tipo de Alarme"], ["value", "Medição"], ["timestamp", "Data"]]

  offset = 10
  slope = 3

  lineChartData: any = null

  constructor() { }

  ngOnInit(): void {
    this.getStatusHistory()
  }

  return() {
    this.onExit.emit()
  }

  setLineData(dataArr: any) {
    if (dataArr.length == 0) {
      this.lineChartData = null
      return;
    }
    this.lineChartData = []
    this.lineChartData.push({
      label: this.sensorInfo?.name,
      realName: this.sensorInfo?.name,
      borderColor: this.sensorInfo?.color,
      backgroundColor: this.sensorInfo?.color + '0A',
      tension: 0.3,
      fill: false,
      data: []
    });

    let newSeries: { x: number, y: number }[] = [];

    for (let info of dataArr) {
      let timestamp = info['timestamp'];
      if (timestamp && !isNaN(new Date(timestamp).getTime())) {
        let dt = new Date(timestamp);
        newSeries.push({ x: dt.getTime(), y: info["value"] });
      } else {
        console.error('Invalid timestamp:', timestamp); // Debugging
      }
    }

    // Update chart data and trigger Angular change detection
    this.lineChartData[0].data = newSeries;
  }

  getCurrentValue() {
    return this.currentReading && this.currentReading != "" ? this.currentReading : "???"
  }

  getStatusHistory() {
    let gtw = this.sensorInfo?.gateway == "*" ? "" : this.sensorInfo?.gateway
    this.onLoad.emit({ "gateway": gtw, "table": this.sensorInfo?.topic, "indicator": this.sensorInfo?.indicator })
  }

}
