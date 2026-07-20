# P1 test instrumentation and data path

**Status:** accepted purchasing candidate; availability checks remain  
**Version:** 0.2
**Date:** 2026-07-20

## 1. Purpose

Close the measurement design for the P1 single-drive bench so the 1,000-cycle
gate can produce evidence rather than a visual judgement. This specification
selects functional candidates; it does not authorize a purchase. Exact supplier,
revision, availability and delivered interfaces must be confirmed first.

## 2. Selected measurement chain

| Function | Candidate | Required configuration / rationale |
|---|---|---|
| Deterministic Pulse+Direction and external encoder capture | Mesa `7I96S` with LinuxCNC >= 2.8.4 | Five differential 5 V step/dir channels and one quadrature encoder input. Use only as P1 bench apparatus, not as a final robot-controller decision. Supply from a dedicated regulated 5.0 V / >=1 A source; the manual permits only 4.75–5.25 V and states up to 400 mA without external loads. |
| Servo diagnostics from Python | Waveshare `USB TO RS485 (C)`, SKU 34620 | Isolated FT232RNL adapter, A/B/GND interface and Linux support. It provides a separate Modbus RTU path for actual position, bus voltage, temperature and alarms. |
| Independent output angle | US Digital `E6-10000-787-IE-D-H-D-3` purchasing configuration to be confirmed, plus screened flying-lead cable | 10,000 CPR, 20 mm bore, differential 5 V output and index. 40,000 quadrature counts/rev gives `0.009 deg/count`, below the required `0.02 deg` measurement resolution. Mount on the rear extension of the output shaft. |
| Temperature logger | Pico Technology `USB TC-08`, order code PP222 | Eight thermocouple channels, Linux SDK and published accuracy. Use attached type-K surface probes on the servo/drive housing, output bearing housing and braking resistor, plus ambient; hand-held contact during the automatic test is not accepted. |
| Belt installation tension | Gates force-deflection method with Mark-10 `M3-5`, 25 N range and 0.02 N resolution | Deflect the measured free span by `span / 64` and record the force. The exact acceptable force is calculated from the Gates procedure and confirmed on the installed drive; no guessed sonic-frequency target is allowed. |

Primary technical sources:

- Mesa 7I96S manual: <https://www.mesanet.com/pdf/parallel/7i96sman.pdf>
- Mesa manufacturer store page: <https://store.mesanet.com/index.php?product_id=374&route=product%2Fproduct>
- Leadshine iSV2-RS manual V2.01: <https://www.leadshine.com/upfiles/downloads/f85ab001e8edd4c7f05e5c32ea6671fd_1766721032370.pdf>
- Waveshare USB TO RS485 (C): <https://docs.waveshare.com/USB_TO_RS485_C>
- US Digital E6: <https://www.usdigital.com/products/encoders/incremental/kit/e6/>
- Pico USB TC-08: <https://www.picotech.com/data-logger/tc-08/usb-tc-08-specifications>
- Gates GT3 drive design manual: <https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf>
- Mark-10 Series 3 force gauge: <https://mark-10.com/products/force-gauges/series-3/>

## 3. Signals and authoritative records

The bench runner remains the owner of timestamps and the combined CSV/JSON
report. Each sample records, when supported by the delivered revision:

- commanded motor and output position;
- Leadshine actual position, position deviation, DC-bus voltage, driver
  temperature and alarm register over Modbus;
- independent E6 output position captured by the motion interface;
- TC-08 temperatures and ambient channel;
- test phase, cycle index and monotonic timestamp.

The E6 measurement is the oracle for output lost motion. The motor's internal
encoder cannot expose compliance or slip downstream of the reduction and must
not be used as the only proof of output accuracy.

## 4. Resolution and timing requirements

- external output resolution: `<= 0.02 deg/count` (candidate: `0.009 deg`);
- position samples: at least 200 samples/s for reversal traces, with timestamped
  source updates rather than fabricated interpolation;
- temperature: at least 1 complete set/s; TC-08 channel sequencing is accepted;
- voltage and alarm polling: at least 20 sets/s if the delivered Modbus link can
  sustain it; measured rate is reported if lower;
- clocks: log the monotonic host time and measure observed inter-sample jitter.

These rates are acquisition targets, not claims about achieved hardware timing.

## 5. Failure behavior and gate

The automated run stops and records an incomplete result on drive alarm,
communications loss, stale encoder data, limit violation or operator stop.
Missing samples are explicit null/error records and are never forward-filled for
acceptance. A P1 report is valid only when its hardware inventory includes exact
model/revision/serial information, encoder configuration, calibration evidence,
belt-tension measurement and channel sample-rate statistics.

The functional selection is closed, but procurement remains blocked until:

1. a genuine 7I96S revision and delivered price are confirmed with the
   traceable European supplier found in the dated Poland supplier research;
2. the exact E6 configuration, cable, centring tool and mounting clearance are
   quoted together;
3. the delivered Leadshine revision and Modbus register scaling are confirmed;
4. attached temperature probes are selected and the M3-5 is quoted with a
   calibration certificate containing data; a lower-cost substitute is allowed
   only with 0–25 N coverage, <= 0.05 N resolution and traceable calibration;
5. the regulated 5.0 V supply and the complete Mesa/E6 current budget are
   selected before wiring.

## 6. Outside this decision

- final three-axis controller architecture;
- SIL/PL-rated safety devices;
- final calibration fixture and metrology laboratory procedure;
- buying duplicate equipment before the P1 gate passes.
