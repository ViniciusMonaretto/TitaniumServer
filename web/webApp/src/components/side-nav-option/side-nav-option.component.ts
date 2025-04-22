import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
    selector: 'side-nav-option',
    templateUrl: './side-nav-option.component.html',
    styleUrls: ['./side-nav-option.component.scss'],
    standalone: false
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
