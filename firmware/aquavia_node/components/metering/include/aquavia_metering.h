#ifndef AQUAVIA_METERING_H
#define AQUAVIA_METERING_H
/* Metrologia: contagem bruta, fator versionado e volume calculado ficam separados.
 * C puro, sem dependência de ESP-IDF, para teste no host. */
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t calibration_version;   /* >= 1 */
    double   liters_per_pulse;      /* > 0, específico ao sensor/configuração */
    uint32_t max_plausible_pulses_per_s; /* faixa plausível; acima disso = inválido */
} aq_calibration_t;

typedef struct {
    aq_calibration_t cal;
    uint32_t last_raw;              /* último valor do contador de hardware (32 bits) */
    bool     has_last;
    double   total_liters;          /* acumulado, nunca decresce */
} aq_meter_t;

typedef struct {
    double volume_delta_liters;
    double flow_lpm;
    bool   valid;                   /* false => não participa de agregados; total preservado */
} aq_sample_t;

bool aq_calibration_valid(const aq_calibration_t *c);
bool aq_meter_init(aq_meter_t *m, const aq_calibration_t *c, double restored_total_liters);
/* raw_counter: contador livre de 32 bits (rollover tratado); dt_ms: intervalo monotônico. */
aq_sample_t aq_meter_update(aq_meter_t *m, uint32_t raw_counter, uint32_t dt_ms);
#endif
