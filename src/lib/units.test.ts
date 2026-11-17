import { fromKg, kgToLb, lbToKg, toKg } from './units';

describe('units', () => {
  test('1 lb is exactly 0.45359237 kg', () => {
    expect(lbToKg(1)).toBe(0.45359237);
  });

  test('converts kg to lb', () => {
    expect(kgToLb(100)).toBeCloseTo(220.462, 3);
  });

  test('round trip keeps the value', () => {
    expect(lbToKg(kgToLb(82.5))).toBeCloseTo(82.5, 10);
  });

  test('fromKg and toKg leave kg unchanged', () => {
    expect(fromKg(60, 'kg')).toBe(60);
    expect(toKg(60, 'kg')).toBe(60);
  });

  test('fromKg and toKg convert pounds', () => {
    expect(fromKg(lbToKg(135), 'lb')).toBeCloseTo(135, 10);
    expect(toKg(135, 'lb')).toBeCloseTo(61.235, 3);
  });
});
