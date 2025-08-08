import { Injectable } from '@angular/core';
import { ServerConectorService } from './server-conector.service';
import { EventAlarmModule } from '../models/event-alarm-module';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { QuestionDialogComponent } from '../components/question-dialog/question-dialog.component';
import { ErrorDialogComponent } from '../components/error-dialog/error-dialog.component';
import { SpinnerComponent } from '../components/spinner/spinner.component';
import { InfoDialogComponent } from '../components/info-dialog/info-dialog.component';

@Injectable({
    providedIn: 'root'
})
export class DialogHelper {
    private dialogRef: MatDialogRef<SpinnerComponent> | null = null;
    constructor(private dialog: MatDialog) { }

    public openQuestionDialog(title: string, message: string, okCallback: Function): void {
        this.dialog.open(QuestionDialogComponent, {
            width: '400px',
            data: {
                message: message,
                title: title,
                onOk: okCallback
            },
        });
    }

    public openErrorDialog(message: string): void {
        this.dialog.open(ErrorDialogComponent, {
            width: '400px',
            data: { message: message },
        });
    }

    public openInfoDialog(message: string, title: string): void {
      this.dialog.open(InfoDialogComponent, {
          width: '400px',
          data: { message: message, title: title },
      });
  }


    public showSpinnerDialog(): void {
        if (!this.dialogRef) {
          this.dialogRef = this.dialog.open(SpinnerComponent, {
            disableClose: true,
            panelClass: 'transparent-dialog',
            backdropClass: 'dimmed-backdrop',
          });
        }
    
      }
    
      public hideSpinnerDialog(): void {
        this.dialogRef?.close();
        this.dialogRef = null;
      }
}