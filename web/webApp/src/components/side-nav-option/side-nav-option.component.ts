import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'side-nav-option',
    templateUrl: './side-nav-option.component.html',
    styleUrls: ['./side-nav-option.component.scss'],
    imports: [CommonModule, MatIconModule],
    standalone: true
})
export class SideNavOptionComponent implements OnInit {

  @Input() icon: string = "";
  @Input() componentText: string = "";
  @Input() isSuboption: boolean = false;
  @Output() buttonCallback: EventEmitter<any> = new EventEmitter();

  unfoldOptions: boolean = false
  

  constructor() { }

  ngOnInit(): void {
  }

  buttonCLick() : void {
    if(!this.buttonCallback.observers.length)
    {
      this.unfoldOptions = !this.unfoldOptions;
    }
    else
    {
      this.buttonCallback.emit()
    }
    
  }

}
