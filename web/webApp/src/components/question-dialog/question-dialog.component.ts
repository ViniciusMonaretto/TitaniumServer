import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { IoButtonComponent } from '../io-button/io-button.component';
  
@Component({
    selector: 'app-error-dialog',
    templateUrl: './question-dialog.component.html',
    styleUrls: ['./question-dialog.component.scss'],
    imports: [CommonModule, MatDialogModule, IoButtonComponent],
    standalone: true
})
export class QuestionDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<QuestionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { message: string, title: string, onOk: Function }
  ) {}

  onOk()
  {
    this.data.onOk()
    this.closeDialog()
  }

  closeDialog(): void {
    this.dialogRef.close();
  }
}