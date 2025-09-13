import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { provideCharts } from 'ng2-charts';  // Correct function: provideCharts

import { routes } from './app.routes';
import { WS_URL_TOKEN } from '../services/server-conector.service';

// Factory function to create WebSocket URL based on current browser location
function createWebSocketUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/websocket`;
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideCharts(),
    { provide: WS_URL_TOKEN, useFactory: createWebSocketUrl }
  ]
};
