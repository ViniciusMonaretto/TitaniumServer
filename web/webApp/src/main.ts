import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import zoomPlugin from 'chartjs-plugin-zoom';
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler,
  Decimation
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Registro manual dos componentes usados no gráfico
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale, // <- isso aqui é essencial!
  Title,
  Tooltip,
  Legend,
  Filler,
  Decimation,
  zoomPlugin
);


bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
