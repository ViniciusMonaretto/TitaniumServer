import { TestBed } from '@angular/core/testing';

import { ConectorService } from './conector.service';

describe('ConectorService', () => {
  let service: ConectorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConectorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
