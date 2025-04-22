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
  @Output() buttonCallback: EventEmitter<any> = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  buttonCLick() : void {
    this.buttonCallback.emit()
  }

}
