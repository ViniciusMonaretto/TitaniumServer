import { Component, Inject, HostListener, ElementRef } from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef, MatDialogModule} from '@angular/material/dialog';
import {SensorTypesEnum} from "../../enum/sensor-type"
import {SensorModule} from "../../models/sensor-module"

import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';

import { ColorChromeModule } from 'ngx-color/chrome';
import { SensorAddWindowComponent } from '../sensor-add-window/sensor-add-window.component';


@Component({
    selector: 'app-group-add-window',
    templateUrl: './group-add-window.component.html',
    styleUrls: ['./group-add-window.component.scss'],
    imports: [CommonModule,
        MatFormFieldModule,
        MatSelectModule,
        MatInputModule,
        FormsModule,
        MatDatepickerModule,
        MatDialogModule,
        ColorChromeModule],
    standalone: true
})
export class GroupAddWindowComponent {
  public groupName: boolean = false

  constructor(public dialogRef: MatDialogRef<SensorAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private elementRef: ElementRef
  ) {

  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  getSensorData()
  {
    if(this.settedType != undefined)
      this.sensorModule.sensorType = this.settedType
    return {
      "name": this.sensorModule.name,
      "gateway": this.sensorModule.gateway,
      "topic": this.sensorModule.topic,
      "sensorType": this.sensorModule.sensorType,
      "group": this.group,
      "indicator": this.sensorModule.indicator,
      "color": this.sensorModule.color
    }
  }

  validForm()
  {
    return this.sensorModule.name != "" &&
           this.sensorModule.gateway != "" &&
           this.sensorModule.topic != "" &&
           this.sensorModule.indicator >= 0 
  }

  onAddCLick(): void{
    this.data.callback(this.getSensorData())
    this.dialogRef.close();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    if (this.showPicker) {
      const clickedElement = event.target as HTMLElement;
      const colorPickerElement = this.elementRef.nativeElement.querySelector('color-chrome');
      const inputElement = this.elementRef.nativeElement.querySelector('input[readonly]');
      
      // Check if click is outside both the color picker and the input field
      if (colorPickerElement && !colorPickerElement.contains(clickedElement) && 
          inputElement && !inputElement.contains(clickedElement)) {
        this.showPicker = false;
      }
    }
  }

}
