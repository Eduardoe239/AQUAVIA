/* Sprint 3 integra sensor_task, queue_task e sync_task (docs: Firmware §5).
 * Por ora apenas o estado inicial da máquina de estados. */
#include "aquavia_metering.h"

typedef enum { ST_BOOT, ST_SELF_TEST, ST_PROVISIONING, ST_CONNECTING, ST_MEASURING,
               ST_SYNCING, ST_DEGRADED, ST_SENSOR_FAULT } aq_state_t;

void app_main(void) {
    aq_state_t state = ST_BOOT;
    (void)state;
}
