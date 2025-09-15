import { Component, Input, Output, EventEmitter, HostBinding, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
export type ButtonSize = 'small' | 'medium' | 'large';
export type ButtonType = 'button' | 'submit' | 'reset';

@Component({
  selector: 'io-button',
  templateUrl: './io-button.component.html',
  styleUrls: ['./io-button.component.scss'],
  imports: [CommonModule, MatIconModule],
  standalone: true,
  encapsulation: ViewEncapsulation.None
})
export class IoButtonComponent {
  @Input() variant: ButtonVariant = 'primary';
  @Input() size: ButtonSize = 'medium';
  @Input() type: ButtonType = 'button';
  @Input() disabled: boolean = false;
  @Input() loading: boolean = false;
  @Input() fullWidth: boolean = false;
  @Input() icon: string = '';
  @Input() iconPosition: 'left' | 'right' = 'left';
  @Input() ariaLabel: string = '';

  @Output() clicked = new EventEmitter<Event>();

  @HostBinding('class')
  get hostClasses(): string {
    const classes = [
      'io-button',
      `io-button--${this.variant}`,
      `io-button--${this.size}`,
      this.fullWidth ? 'io-button--full-width' : '',
      this.disabled ? 'io-button--disabled' : '',
      this.loading ? 'io-button--loading' : ''
    ].filter(Boolean).join(' ');
    console.log('Host classes:', classes);
    return classes;
  }

  onClick(event: Event): void {
    if (!this.disabled && !this.loading) {
      this.clicked.emit(event);
    }
  }

  get buttonClasses(): string {
    const classes = [
      'io-button__element',
      this.icon && !this.loading ? 'io-button__element--with-icon' : '',
      this.iconPosition === 'right' ? 'io-button__element--icon-right' : ''
    ].filter(Boolean).join(' ');
    console.log('Button classes:', classes, 'Variant:', this.variant);
    return classes;
  }
}