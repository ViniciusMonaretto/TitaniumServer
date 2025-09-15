import { Component, OnInit } from '@angular/core';
import { ServerConectorService } from "../../services/server-conector.service"
import { UiPanelService } from "../../services/ui-panels.service"
import { MatDialog } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { GatewayInfoTabComponent } from '../../components/gateway-info-tab/gateway-info-tab.component';
import { GatewayModule } from '../../models/gateway-model';
import { IoButtonComponent } from '../../components/io-button/io-button.component';

@Component({
    selector: 'gateway-screen',
    templateUrl: './gateway-screen.component.html',
    styleUrls: ['./gateway-screen.component.scss'],
    imports: [CommonModule, GatewayInfoTabComponent, IoButtonComponent],
    standalone: true
})
export class GatewayScreenComponent implements OnInit {

  constructor(public dialog: MatDialog, private connectorService: ServerConectorService, private uiPanelService: UiPanelService) {
    
  }

  updateGateways(): void {
    this.connectorService.sendCommand("updateGateways", {})
  }

  getGateways(): GatewayModule[] {
    return this.uiPanelService.gateways
  }

  ngOnInit(): void {
  }
}   