import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { provideCharts } from 'ng2-charts';  // Correct function: provideCharts

import { routes } from './app.routes';
import { WS_URL_TOKEN } from '../services/server-conector.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideCharts(),
    { provide: WS_URL_TOKEN, useValue: 'ws://localhost:8888/websocket' }
  ]
};
