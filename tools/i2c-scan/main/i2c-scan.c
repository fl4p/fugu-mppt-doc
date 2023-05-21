/* i2c - Scan for devices on the bus
*/
#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"

static const char *TAG = "i2c-scan";

#define I2C_MASTER_SCL_IO           22      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA_IO           21      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */
#define I2C_MASTER_FREQ_HZ          400000                     /*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_RX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_TIMEOUT_MS       1000

#define I2C_BUFFER_LENGTH 128

static esp_err_t i2c_master_init(void) {
    int i2c_master_port = I2C_MASTER_NUM;

    i2c_config_t conf = {
            .mode = I2C_MODE_MASTER,
            .sda_io_num = I2C_MASTER_SDA_IO,
            .scl_io_num = I2C_MASTER_SCL_IO,
            .sda_pullup_en = GPIO_PULLUP_ENABLE,
            .scl_pullup_en = GPIO_PULLUP_ENABLE,
            .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };

    i2c_param_config(i2c_master_port, &conf);

    return i2c_driver_install(i2c_master_port, conf.mode, I2C_MASTER_RX_BUF_DISABLE, I2C_MASTER_TX_BUF_DISABLE, 0);
}

esp_err_t i2cWrite(uint8_t i2c_num, uint16_t address, const uint8_t *buff, size_t size, uint32_t timeOutMillis) {
    esp_err_t ret = ESP_FAIL;
    i2c_cmd_handle_t cmd = NULL;

    //short implementation does not support zero size writes (example when scanning) PR in IDF?
    //ret =  i2c_master_write_to_device((i2c_port_t)i2c_num, address, buff, size, timeOutMillis / portTICK_RATE_MS);

    ret = ESP_OK;
    uint8_t cmd_buff[I2C_LINK_RECOMMENDED_SIZE(1)] = {0};
    cmd = i2c_cmd_link_create_static(cmd_buff, I2C_LINK_RECOMMENDED_SIZE(1));
    ret = i2c_master_start(cmd);
    if (ret != ESP_OK) {
        goto end;
    }
    ret = i2c_master_write_byte(cmd, (address << 1) | I2C_MASTER_WRITE, true);
    if (ret != ESP_OK) {
        goto end;
    }
    if (size) {
        ret = i2c_master_write(cmd, buff, size, true);
        if (ret != ESP_OK) {
            goto end;
        }
    }
    ret = i2c_master_stop(cmd);
    if (ret != ESP_OK) {
        goto end;
    }
    ret = i2c_master_cmd_begin((i2c_port_t) i2c_num, cmd, timeOutMillis / portTICK_PERIOD_MS);

    end:
    if (cmd != NULL) {
        i2c_cmd_link_delete_static(cmd);
    }
    return ret;
}

void i2cScan() {
    int numDevices = 0;
    uint8_t txBuf[2];

    ESP_LOGI(TAG, "Scanning 0..0x%02hhX ...", 127);
    for (uint8_t address = 1; address < 127; ++address) {
        esp_err_t err = i2cWrite(I2C_MASTER_NUM, address, txBuf, 0, 50);
        switch (err) {
            case ESP_OK:
                ESP_LOGI(TAG, "Device found at address 0x%02hhX (%u)", address, address);
                ++numDevices;
            case ESP_FAIL:
                break;
            case ESP_ERR_TIMEOUT:
                break;
            default:
                break;
        }
    }

    ESP_LOGI(TAG, "Scan complete. Found %d I2C devices", numDevices);
}


void app_main(void) {
    ESP_ERROR_CHECK(i2c_master_init());
    ESP_LOGI(TAG, "I2C initialized successfully");


    while (1) {
        i2cScan();
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}
