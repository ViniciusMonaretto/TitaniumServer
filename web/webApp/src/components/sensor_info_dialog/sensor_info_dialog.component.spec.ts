import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SensorTypesEnum } from '../../enum/sensor-type';
import { SensorModule } from '../../models/sensor-module';
import { SensorInfoDialogComponent } from './sensor_info_dialog.component';

describe('SensorInfoDialogComponent', () => {
  let callback: jasmine.Spy
  let dialogRef: jasmine.SpyObj<MatDialogRef<SensorInfoDialogComponent>>

  function makeSensor(overrides: Partial<SensorModule> = {}): SensorModule {
    return Object.assign(new SensorModule(), {
      id: 7,
      name: "Pressure",
      gateway: "gw1",
      topic: "pressure",
      color: "#0000FF",
      indicator: 0,
      sensorType: SensorTypesEnum.PREASSURE,
      gain: 1,
      offset: 0,
      multiplier: 1
    }, overrides)
  }

  function create(sensor: SensorModule, canEdit = true): ComponentFixture<SensorInfoDialogComponent> {
    TestBed.overrideProvider(MAT_DIALOG_DATA, { useValue: { sensorInfo: sensor, callback, canEdit } })
    const fixture = TestBed.createComponent(SensorInfoDialogComponent)
    fixture.detectChanges()
    return fixture
  }

  beforeEach(async () => {
    callback = jasmine.createSpy('callback')
    dialogRef = jasmine.createSpyObj('MatDialogRef', ['close'])
    await TestBed.configureTestingModule({
      imports: [SensorInfoDialogComponent],
      providers: [
        { provide: MatDialogRef, useValue: dialogRef },
        { provide: MAT_DIALOG_DATA, useValue: {} }
      ]
    }).compileComponents()
  });

  describe('loading the sensor', () => {
    it('reads the pressure range and unit', () => {
      const dialog = create(makeSensor({ zeroValue: 0, maxValue: 10, pressureUnit: "bar" })).componentInstance
      expect(dialog.isPressure).toBeTrue()
      expect(dialog.enableRange).toBeTrue()
      expect(dialog.zeroValue).toBe(0)
      expect(dialog.maxValue).toBe(10)
      expect(dialog.pressureUnit).toBe("bar")
      expect(dialog.baseUnit).toBe("bar")
    });

    it('defaults to Pa without a range', () => {
      const dialog = create(makeSensor()).componentInstance
      expect(dialog.enableRange).toBeFalse()
      expect(dialog.pressureUnit).toBe("Pa")
      expect(dialog.baseUnit).toBe("Pa")
    });

    it('keeps the range disabled when only one end is set', () => {
      const dialog = create(makeSensor({ zeroValue: 0 })).componentInstance
      expect(dialog.enableRange).toBeFalse()
    });

    it('does not treat other sensors as pressure', () => {
      const dialog = create(makeSensor({ sensorType: SensorTypesEnum.TEMPERATURE, zeroValue: 0, maxValue: 10 })).componentInstance
      expect(dialog.isPressure).toBeFalse()
      expect(dialog.enableRange).toBeFalse()
      expect(dialog.baseUnit).toBe("ºC")
    });
  });

  describe('kilo option', () => {
    it('is available for Pa', () => {
      expect(create(makeSensor()).componentInstance.canUseKilo()).toBeTrue()
    });

    it('is available for non pressure sensors', () => {
      expect(create(makeSensor({ sensorType: SensorTypesEnum.POWER })).componentInstance.canUseKilo()).toBeTrue()
    });

    it('is not available for psi or bar', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.pressureUnit = "psi"
      expect(dialog.canUseKilo()).toBeFalse()
      dialog.pressureUnit = "bar"
      expect(dialog.canUseKilo()).toBeFalse()
    });

    it('drops the kilo multiplier when switching to bar', () => {
      const dialog = create(makeSensor({ multiplier: 1000 })).componentInstance
      expect(dialog.kiloSelected).toBeTrue()
      dialog.pressureUnit = "bar"
      expect(dialog.getChangeInfoPanel()["multiplier"]).toBe(1)
    });
  });

  describe('range validation', () => {
    it('accepts a disabled range', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.enableRange = false
      dialog.zeroValue = 10
      dialog.maxValue = 0
      expect(dialog.validRange()).toBeTrue()
    });

    it('requires max to be greater than zero', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.enableRange = true
      dialog.zeroValue = 0
      dialog.maxValue = 10
      expect(dialog.validRange()).toBeTrue()
      dialog.maxValue = 0
      expect(dialog.validRange()).toBeFalse()
      dialog.maxValue = -1
      expect(dialog.validRange()).toBeFalse()
    });

    it('requires both ends when enabled', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.enableRange = true
      dialog.zeroValue = 0
      dialog.maxValue = null
      expect(dialog.validRange()).toBeFalse()
      dialog.zeroValue = undefined
      dialog.maxValue = 10
      expect(dialog.validRange()).toBeFalse()
    });

    it('blocks applying an invalid range', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.enableRange = true
      dialog.zeroValue = 10
      dialog.maxValue = 5
      expect(dialog.validForm()).toBeFalse()
    });
  });

  describe('change detection', () => {
    function unchangedDialog(sensor: SensorModule) {
      const dialog = create(sensor).componentInstance
      // Without these the form is always applicable
      dialog.calibrate = false
      dialog.enableAlarms = false
      return dialog
    }

    it('has nothing to apply when unchanged', () => {
      const dialog = unchangedDialog(makeSensor({ zeroValue: 0, maxValue: 10, pressureUnit: "bar" }))
      expect(dialog.isRangeDifferent()).toBeFalse()
      expect(dialog.isPressureUnitDifferent()).toBeFalse()
      expect(dialog.validForm()).toBeFalse()
    });

    it('treats a missing unit as Pa', () => {
      const dialog = unchangedDialog(makeSensor({ pressureUnit: null }))
      expect(dialog.isPressureUnitDifferent()).toBeFalse()
    });

    it('can apply a new pressure unit', () => {
      const dialog = unchangedDialog(makeSensor())
      dialog.pressureUnit = "psi"
      expect(dialog.isPressureUnitDifferent()).toBeTrue()
      expect(dialog.validForm()).toBeTrue()
    });

    it('can apply a new range', () => {
      const dialog = unchangedDialog(makeSensor())
      dialog.enableRange = true
      dialog.zeroValue = 0
      dialog.maxValue = 10
      expect(dialog.isRangeDifferent()).toBeTrue()
      expect(dialog.validForm()).toBeTrue()
    });

    it('can apply removing the range', () => {
      const dialog = unchangedDialog(makeSensor({ zeroValue: 0, maxValue: 10 }))
      dialog.enableRange = false
      expect(dialog.isRangeDifferent()).toBeTrue()
      expect(dialog.validForm()).toBeTrue()
    });

    it('cannot apply when not editable', () => {
      const dialog = create(makeSensor(), false).componentInstance
      dialog.pressureUnit = "bar"
      expect(dialog.validForm()).toBeFalse()
    });
  });

  describe('applying', () => {
    it('sends the range and unit for pressure sensors', () => {
      const dialog = create(makeSensor()).componentInstance
      dialog.pressureUnit = "bar"
      dialog.enableRange = true
      dialog.zeroValue = 1
      dialog.maxValue = 6
      dialog.onApply()

      expect(callback).toHaveBeenCalledOnceWith(jasmine.objectContaining({
        panelId: 7,
        pressureUnit: "bar",
        zeroValue: 1,
        maxValue: 6
      }))
      expect(dialogRef.close).toHaveBeenCalled()
    });

    it('sends no range when it is disabled', () => {
      const dialog = create(makeSensor({ zeroValue: 0, maxValue: 10 })).componentInstance
      dialog.enableRange = false
      const info = dialog.getChangeInfoPanel()
      expect(info["zeroValue"]).toBeNull()
      expect(info["maxValue"]).toBeNull()
      expect(info["pressureUnit"]).toBe("Pa")
    });

    it('sends no range or unit for other sensors', () => {
      const dialog = create(makeSensor({ sensorType: SensorTypesEnum.POWER })).componentInstance
      dialog.enableRange = true
      dialog.zeroValue = 0
      dialog.maxValue = 10
      const info = dialog.getChangeInfoPanel()
      expect(info["zeroValue"]).toBeNull()
      expect(info["maxValue"]).toBeNull()
      expect(info["pressureUnit"]).toBeNull()
    });
  });

  describe('template', () => {
    function text(fixture: ComponentFixture<SensorInfoDialogComponent>): string {
      return (fixture.nativeElement as HTMLElement).textContent ?? ""
    }

    it('shows the unit selector and range for pressure', () => {
      const pressure = create(makeSensor())
      expect(text(pressure)).toContain("Unidade de medida")
      expect(text(pressure)).toContain("Mapear faixa do sensor")
      expect(pressure.nativeElement.querySelector('mat-select')).toBeTruthy()
    });

    it('hides the unit selector and range for other sensors', () => {
      const power = create(makeSensor({ sensorType: SensorTypesEnum.POWER }))
      expect(text(power)).not.toContain("Unidade de medida")
      expect(text(power)).not.toContain("Mapear faixa do sensor")
    });

    it('labels the range inputs with the chosen unit', () => {
      const fixture = create(makeSensor({ zeroValue: 0, maxValue: 10, pressureUnit: "psi" }))
      expect(text(fixture)).toContain("Zero (psi)")
      expect(text(fixture)).toContain("Máximo (psi)")
    });

    it('hides the kilo option for bar', () => {
      const fixture = create(makeSensor())
      expect(text(fixture)).toContain("Mostrar em Kilo")
      fixture.componentInstance.pressureUnit = "bar"
      fixture.detectChanges()
      expect(text(fixture)).not.toContain("Mostrar em Kilo")
    });

    it('warns about an invalid range', () => {
      const fixture = create(makeSensor())
      fixture.componentInstance.enableRange = true
      fixture.componentInstance.zeroValue = 10
      fixture.componentInstance.maxValue = 5
      fixture.detectChanges()
      expect(text(fixture)).toContain("O valor máximo deve ser maior que o zero.")
    });
  });
});
