import { Component, Inject, ElementRef } from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef, MatDialogModule} from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';

import { SensorAddWindowComponent } from '../sensor-add-window/sensor-add-window.component';


@Component({
    selector: 'app-group-add-window',
    templateUrl: './group-add-window.component.html',
    styleUrls: ['./group-add-window.component.scss'],
    imports: [CommonModule,
        MatFormFieldModule,
        MatInputModule,
        FormsModule,
        MatDialogModule],
    standalone: true
})
export class GroupAddWindowComponent {
  public groupName: string = ""

  constructor(public dialogRef: MatDialogRef<GroupAddWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private elementRef: ElementRef
  ) {

  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  getGroupData()
  {
    return {
      "name": this.groupName
    }
  }

  validForm()
  {
    return this.groupName != "" 
  }

  onAddCLick(): void{
    this.data.callback(this.getGroupData())
    this.dialogRef.close();
  }

  onCancelClick(): void{
    this.dialogRef.close();
  }

}
