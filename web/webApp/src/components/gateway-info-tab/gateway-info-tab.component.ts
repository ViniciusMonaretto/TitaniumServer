import { Component,  Input, } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GatewayModule } from '../../models/gateway-model';

@Component({
  selector: 'gateway-info-tab',
  imports: [CommonModule],
  templateUrl: './gateway-info-tab.component.html',
  styleUrl: './gateway-info-tab.component.scss',
  standalone: true
})
export class GatewayInfoTabComponent {
  @Input() gatewayInfo: GatewayModule = new GatewayModule()

  /**
   * Checks if the gateway is online based on uptime
   * A gateway is considered online if uptime > 0
   */
  isGatewayOnline(): boolean {
    return this.gatewayInfo.uptime > 0;
  }

  /**
   * Formats uptime in milliseconds to a human-readable format
   * @param uptimeMilliseconds - Uptime in milliseconds
   * @returns Formatted uptime string
   */
  formatUptime(uptimeMilliseconds: number): string {
    if (uptimeMilliseconds <= 0) {
      return 'Offline';
    }

    // Convert milliseconds to seconds
    const uptimeSeconds = Math.floor(uptimeMilliseconds / 1000);
    
    const days = Math.floor(uptimeSeconds / 86400);
    const hours = Math.floor((uptimeSeconds % 86400) / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);
    const seconds = uptimeSeconds % 60;

    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (seconds > 0 && days === 0) parts.push(`${seconds}s`);

    return parts.length > 0 ? parts.join(' ') : '0s';
  }
}
