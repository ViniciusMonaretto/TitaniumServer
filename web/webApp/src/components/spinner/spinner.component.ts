import { Component, ElementRef, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'app-spinner-dialog',
    templateUrl: './spinner.component.html',
    styleUrls: ['./spinner.component.scss'],
    imports: [CommonModule, MatProgressSpinnerModule],
    standalone: true
})
export class SpinnerComponent {

    message: string = ""
    dotCount: number = 0
    timedFunction: any
    constructor(public dialogRef: MatDialogRef<SpinnerComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        private elementRef: ElementRef
    ) {
        this.message = data.message
        if(this.data.addDots)
        {
            this.addTimedDots()
        }
    }

    ngOnDestroy()
    {
        if (this.timedFunction)
        {
            clearInterval(this.timedFunction)
        }
    }

    addTimedDots()
    {
        this.timedFunction = setInterval(() => {
            this.dotCount++
            if(this.dotCount > 3)
            {
                this.dotCount = 0
                this.message = this.message.slice(0, -3)
            }
            else
            {
                 this.message = this.message + "."
            }
        }, 1000)
    }



}