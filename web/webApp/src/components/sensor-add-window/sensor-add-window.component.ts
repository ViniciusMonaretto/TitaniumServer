import { Component, OnInit } from '@angular/core';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'app-sensor-add-window',
  templateUrl: './sensor-add-window.component.html',
  styleUrls: ['./sensor-add-window.component.scss']
})
export class SensorAddWindowComponent {

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>) {
    
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

}
