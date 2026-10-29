#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "aquavia_metering.h"

static int near(double a, double b) { return fabs(a - b) < 1e-9; }

int main(void) {
    aq_calibration_t cal = {3, 0.002, 200};   /* 2 mL/pulso */
    aq_meter_t m;
    assert(!aq_calibration_valid(&(aq_calibration_t){0, 0.002, 200}));
    assert(!aq_meter_init(&m, &cal, -1.0));
    assert(aq_meter_init(&m, &cal, 100.0));

    aq_sample_t s = aq_meter_update(&m, 1000, 1000);       /* baseline */
    assert(!s.valid && near(m.total_liters, 100.0));

    s = aq_meter_update(&m, 1500, 60000);                   /* 500 pulsos em 60 s */
    assert(s.valid && near(s.volume_delta_liters, 1.0) && near(s.flow_lpm, 1.0));
    assert(near(m.total_liters, 101.0));

    s = aq_meter_update(&m, 1500 + 100000, 1000);           /* 100k pps: implausível */
    assert(!s.valid && near(m.total_liters, 101.0));        /* total preservado */

    aq_meter_init(&m, &cal, 0.0);                           /* rollover de 32 bits */
    aq_meter_update(&m, 0xFFFFFF00u, 1000);
    s = aq_meter_update(&m, 0x00000064u, 10000);            /* 356 pulsos */
    assert(s.valid && near(s.volume_delta_liters, 356 * 0.002));

    s = aq_meter_update(&m, 0x00000064u, 0);                /* dt zero: ignora */
    assert(!s.valid);
    puts("metering: ok");
    return 0;
}
