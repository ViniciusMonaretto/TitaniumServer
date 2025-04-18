import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms'; // Import FormsModule

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

//Project Screen Components
import { MainScreenComponent } from 'src/panels/main-screen/main-screen.component';
import { SensorGroupComponent } from 'src/panels/sensor-group/sensor-group.component';
import { NavbarComponent } from 'src/panels/navbar/navbar.component';
import { GraphViewComponent } from 'src/panels/graph-view/graph-view.component'

//Project Components
import { SensorAddWindowComponent } from 'src/components/sensor-add-window/sensor-add-window.component';
import { SensorComponent } from 'src/components/sensor/sensor.component';
import { SideNavOptionComponent } from 'src/components/side-nav-option/side-nav-option.component';
import { GroupOfSensorsComponent } from 'src/components/group-of-sensors/group-of-sensors.component';
import { InfoTableComponent } from 'src/components/info-table/info-table.component';
import {SensorInfoComponent} from  'src/components/sensor-info/sensor-info.component'
import { LoadingComponent } from '../components/loading/loading.component';


//Angular Material
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button'; 
import {MatDialogModule} from '@angular/material/dialog'; 
import {MatFormFieldModule} from '@angular/material/form-field'; 
import { MatSelectModule } from '@angular/material/select'; 
import { MatInputModule } from '@angular/material/input'; 
import {MatCardModule} from '@angular/material/card'; 
import {MatTableModule} from '@angular/material/table'; 
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';

import { NgxChartsModule } from '@swimlane/ngx-charts'



import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ErrorDialogComponent } from 'src/components/error-dialog/error-dialog.component';
import { GraphRequestWindowComponent } from '../components/graph-request-window/graph-request-window.component';
import { GraphComponent } from 'src/components/graph/graph.component';
import { SpinnerComponent } from '../components/spinner/spinner.component';

@NgModule({
  declarations: [
    AppComponent,
    MainScreenComponent,
    SensorComponent,
    SideNavOptionComponent,
    NavbarComponent,
    SensorAddWindowComponent,
    SensorGroupComponent,
    GroupOfSensorsComponent,
    InfoTableComponent,
    GraphViewComponent,
    SensorInfoComponent,
    ErrorDialogComponent,
    GraphRequestWindowComponent,
    GraphComponent,
    LoadingComponent,
    SpinnerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,

    BrowserAnimationsModule,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatCardModule,
    MatTableModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    NgxChartsModule
  ],
  entryComponents: [SensorAddWindowComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
