#include "aquavia_metering.h"

bool aq_calibration_valid(const aq_calibration_t *c) {
    return c && c->calibration_version >= 1 && c->liters_per_pulse > 0.0 &&
           c->max_plausible_pulses_per_s > 0;
}

bool aq_meter_init(aq_meter_t *m, const aq_calibration_t *c, double restored_total_liters) {
    if (!m || !aq_calibration_valid(c) || restored_total_liters < 0.0) return false;
    m->cal = *c; m->last_raw = 0; m->has_last = false; m->total_liters = restored_total_liters;
    return true;
}

aq_sample_t aq_meter_update(aq_meter_t *m, uint32_t raw, uint32_t dt_ms) {
    aq_sample_t s = {0.0, 0.0, false};
    if (!m->has_last) { m->last_raw = raw; m->has_last = true; return s; } /* baseline */
    if (dt_ms == 0) return s;
    uint32_t pulses = raw - m->last_raw;     /* aritmética modular: rollover correto */
    m->last_raw = raw;
    double pps = (double)pulses * 1000.0 / (double)dt_ms;
    if (pps > (double)m->cal.max_plausible_pulses_per_s) return s; /* ruído/glitch: não soma */
    s.volume_delta_liters = (double)pulses * m->cal.liters_per_pulse;
    s.flow_lpm = s.volume_delta_liters / ((double)dt_ms / 60000.0);
    m->total_liters += s.volume_delta_liters;
    s.valid = true;
    return s;
}
