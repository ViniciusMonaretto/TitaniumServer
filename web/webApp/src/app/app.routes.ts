import { Routes } from '@angular/router';
import { MainScreenComponent } from '../panels/main-screen/main-screen.component';

export const routes: Routes = [
    { path: 'main', component: MainScreenComponent }, // Define the route for MyComponent
    { path: '', redirectTo: '/main', pathMatch: 'full' } // Redirect to a default route
];
