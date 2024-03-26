#!/usr/bin/python3

#
# FTDI FT232H
#
# https://iosoft.blog/2018/12/05/ftdi-python-part-3/
# https://ftdichip.com/wp-content/uploads/2020/08/AN_108_Command_Processor_for_MPSSE_and_MCU_Host_Bus_Emulation_Modes.pdf
# https://ftdichip.com/wp-content/uploads/2023/09/D2XX_Programmers_Guide.pdf
#
# https://libftdi.developer.intra2net.narkive.com/qIRkD5AR/ftdi-read-data-returns-immediately-without-waiting-for-timeout-and-with-no-data
#
# TUSS4470
#
# https://www.ti.com/lit/ds/symlink/tuss4470.pdf?ts=1704475946021
# https://www.ti.com/lit/ug/slau822a/slau822a.pdf?ts=1705051190678
# https://github.com/MikroElektronika/mikrosdk_click_v2/blob/1b1b00b1b58f46c109b7c0386c0396a7daccf125/clicks/ultrasonic5/lib_ultrasonic5/src/ultrasonic5.c
#

import time, sys
import pylibftdi as ftdi

BITMODE_MPSSE = 0x02

MPSSE_WRITE_NEG = 0x01   # Write TDI/DO on negative TCK/SK edge
MPSSE_BITMODE   = 0x02   # Write bits, not bytes
MPSSE_READ_NEG  = 0x04   # Sample TDO/DI on negative TCK/SK edge
MPSSE_LSB       = 0x08   # LSB first
MPSSE_DO_WRITE  = 0x10   # Write TDI/DO
MPSSE_DO_READ   = 0x20   # Read TDO/DI
MPSSE_WRITE_TMS = 0x40   # Write TMS/CS

DIS_3_PHASE     = 0x8d
DIS_ADAPTIVE    = 0x97

# FTDI MPSSE commands
SET_BITS_LOW   = 0x80
SET_BITS_HIGH  = 0x82
GET_BITS_LOW   = 0x81
GET_BITS_HIGH  = 0x83
LOOPBACK_START = 0x84
LOOPBACK_END   = 0x85
TCK_DIVISOR    = 0x86

# H Type specific commands
DIS_DIV_5       = 0x8a
EN_DIV_5        = 0x8b
EN_3_PHASE      = 0x8c
DIS_3_PHASE     = 0x8d
CLK_BITS        = 0x8e
CLK_BYTES       = 0x8f
CLK_WAIT_HIGH   = 0x94
CLK_WAIT_LOW    = 0x95
EN_ADAPTIVE     = 0x96
DIS_ADAPTIVE    = 0x97
CLK_BYTES_OR_HIGH = 0x9c
CLK_BYTES_OR_LOW  = 0x9d

# Pins
# ADBUS
SK_PIN  = 1<<0
DO_PIN  = 1<<1
DI_PIN  = 1<<2
CS_PIN  = 1<<3
IO1_PIN = 1<<4

OUT_PINS = SK_PIN|DO_PIN|CS_PIN|IO1_PIN

#
# TUSS registers
#

# Specified registers list of TUSS driver
TUSS_REG_BPF_CONFIG_1                = 0x10
TUSS_REG_BPF_CONFIG_2                = 0x11
TUSS_REG_DEV_CTRL_1                  = 0x12
TUSS_REG_DEV_CTRL_2                  = 0x13
TUSS_REG_DEV_CTRL_3                  = 0x14
TUSS_REG_VDRV_CTRL                   = 0x16
TUSS_REG_ECHO_INT_CONFIG             = 0x17
TUSS_REG_ZC_CONFIG                   = 0x18
TUSS_REG_BURST_PULSE                 = 0x1A
TUSS_REG_TOF_CONFIG                  = 0x1B
TUSS_REG_DEV_STAT                    = 0x1C
TUSS_REG_DEVICE_ID                   = 0x1D
TUSS_REG_REV_ID                      = 0x1E


# Specified BPF_CONFIG_1 register settings
TUSS_BPF_CONFIG_1_FC_TRIM_FRC        = 0x80
TUSS_BPF_CONFIG_1_BYPASS             = 0x40
TUSS_BPF_CONFIG_1_HPF_FREQ_MASK      = 0x3F
TUSS_BPF_CONFIG_1_RESET              = 0x00

# Specified BPF_CONFIG_2 register settings
TUSS_BPF_CONFIG_2_Q_SEL_4            = 0x00
TUSS_BPF_CONFIG_2_Q_SEL_5            = 0x10
TUSS_BPF_CONFIG_2_Q_SEL_2            = 0x20
TUSS_BPF_CONFIG_2_Q_SEL_3            = 0x30
TUSS_BPF_CONFIG_2_Q_SEL_MASK         = 0x30
TUSS_BPF_CONFIG_2_FC_TRIM_MASK       = 0x0F
TUSS_BPF_CONFIG_2_RESET              = 0x00

# Specified DEV_CTRL_1 register settings
TUSS_DEV_CTRL_1_LOGAMP_FRC           = 0x80
TUSS_DEV_CTRL_1_LOGAMP_SLP_ADJ_MASK  = 0x70
TUSS_DEV_CTRL_1_LOGAMP_INT_ADJ_MASK  = 0x0F
TUSS_DEV_CTRL_1_RESET                = 0x00

# Specified DEV_CTRL_2 register settings
TUSS_DEV_CTRL_2_LOGAMP_DIS_FIRST     = 0x80
TUSS_DEV_CTRL_2_LOGAMP_DIS_LAST      = 0x40
TUSS_DEV_CTRL_2_VOUT_SCALE_SEL_5V    = 0x04
TUSS_DEV_CTRL_2_LNA_GAIN_15V         = 0x00
TUSS_DEV_CTRL_2_LNA_GAIN_10V         = 0x01
TUSS_DEV_CTRL_2_LNA_GAIN_20V         = 0x02
TUSS_DEV_CTRL_2_LNA_GAIN_12_5V       = 0x03
TUSS_DEV_CTRL_2_LNA_GAIN_MASK        = 0x03
TUSS_DEV_CTRL_2_RESET                = 0x00

# Specified DEV_CTRL_3 register settings
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_64US  = 0x00
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_48US  = 0x04
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_32US  = 0x08
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_24US  = 0x0C
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_16US  = 0x10
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_8US   = 0x14
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_4US   = 0x18
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_DIS   = 0x1C
TUSS_DEV_CTRL_3_DRV_PLS_FLT_DT_MASK  = 0x1C
TUSS_DEV_CTRL_3_IO_MODE_0            = 0x00
TUSS_DEV_CTRL_3_IO_MODE_1            = 0x01
TUSS_DEV_CTRL_3_IO_MODE_2            = 0x02
TUSS_DEV_CTRL_3_IO_MODE_3            = 0x03
TUSS_DEV_CTRL_3_IO_MODE_MASK         = 0x03
TUSS_DEV_CTRL_3_RESET                = 0x00

# Specified VDRV_CTRL register settings
TUSS_VDRV_CTRL_DIS_VDRV_REG_LSTN     = 0x40
TUSS_VDRV_CTRL_VDRV_HI_Z             = 0x20
TUSS_VDRV_CTRL_VDRV_CURR_LVL_20MA    = 0x10
TUSS_VDRV_CTRL_VDRV_VOLT_LVL_5V      = 0x00
TUSS_VDRV_CTRL_VDRV_VOLT_LVL_MASK    = 0x0F
TUSS_VDRV_CTRL_RESET                 = 0x20

# Specified ECHO_INT_CONFIG register settings
TUSS_ECHO_INT_CONFIG_CMP_EN          = 0x10
TUSS_ECHO_INT_CONFIG_THR_SEL_MASK    = 0x0F
TUSS_ECHO_INT_CONFIG_RESET           = 0x07

# Specified ZC_CONFIG register settings
TUSS_ZC_CONFIG_CMP_EN                = 0x80
TUSS_ZC_CONFIG_EN_ECHO_INT           = 0x40
TUSS_ZC_CONFIG_CMP_IN_SEL            = 0x20
TUSS_ZC_CONFIG_CMP_STG_SEL_MASK      = 0x18
TUSS_ZC_CONFIG_CMP_HYST_MASK         = 0x07
TUSS_ZC_CONFIG_RESET                 = 0x14

# Specified BURST_PULSE register settings
TUSS_BURST_PULSE_HALF_BRG_MODE       = 0x80
TUSS_BURST_PULSE_PRE_DRIVER_MODE     = 0x40
TUSS_BURST_PULSE_BURST_PULSE_16      = 0x10
TUSS_BURST_PULSE_BURST_PULSE_MASK    = 0x3F
TUSS_BURST_PULSE_RESET               = 0x00

# Specified TOF_CONFIG register settings
TUSS_TOF_CONFIG_SLEEP_MODE_EN        = 0x80
TUSS_TOF_CONFIG_STDBY_MODE_EN        = 0x40
TUSS_TOF_CONFIG_VDRV_TRIGGER         = 0x02
TUSS_TOF_CONFIG_CMD_TRIGGER          = 0x01
TUSS_TOF_CONFIG_RESET                = 0x00

# Specified setting for burst OUTA,OUTB
TUSS_BURST_FREQ                      = 40000

# Specified device ID
TUSS_DEVICE_ID                       = 0xB9

# Specified device read bit
TUSS_SPI_READ_BIT                    = 0x80


def ft_set_clock(d, hz):
    div = int((12000000 / (hz * 2)) - 1)
    ft_write(d, (TCK_DIVISOR, div%256, div//256))

def ft_read(d, nbytes):
    s = d.read(nbytes)
    return list(s)

def ft_write(d, data):
    s = bytes(data)
    r = d.write(s)
    return r

def ft_make_hdr(cmd, n):
    n = n - 1
    return (cmd, n%256, n//256)

def ft_make_mpsse_pkg(cmd, data):
    hdr = ft_make_hdr(cmd, len(data))
    return hdr + tuple(data)

def tuss_calc_parity_bit(data_arr):
    parity = 0
    data_in = (data_arr[0] << 8) | data_arr[1]
    while data_in & 0xFFFE:
        parity += data_in & 1
        data_in >>= 1

    return parity & 1

def tuss_spi_write_read(b1, b2):
    b1 |= tuss_calc_parity_bit([b1, b2])

    ret = ft_write(d,
             # CS low, IO1 high
             (SET_BITS_LOW, IO1_PIN, OUT_PINS) +
             # SPI write-read; out on +ve edge, in on -ve edge
             ft_make_mpsse_pkg(MPSSE_DO_READ | MPSSE_DO_WRITE | MPSSE_WRITE_NEG, [b1, b2]) +
             # CS|IO1 high, other low
             (SET_BITS_LOW, CS_PIN|IO1_PIN, OUT_PINS))
    if ret != 11:
        return (-1, 0x00)

    rd = ft_read(d, 2)
    if len(rd) != 2:
        return (-1, 0x00)
    if rd[0] & 0x80:
        print("Error: parity error set")
        return (-1, 0x00)

    status = (rd[0] >> 1) & ((1<<5)-1)

    return (status, rd[1])

def tuss_read_register(reg):
    b1 = TUSS_SPI_READ_BIT | ((reg & 0x3F) << 1)
    b2 = 0x00

    return tuss_spi_write_read(b1, b2)

def tuss_write_register(reg, data_in):
    b1 = (reg & 0x3F) << 1
    b2 = data_in

    rd = tuss_spi_write_read(b1, b2)
    if rd[1] != b1:
        return -1

    return 0

def tuss_default_setup():
    # Set SPI clock frequency
    ft_set_clock(d, 1e6)

    rd = tuss_read_register(TUSS_REG_DEVICE_ID)
    if rd[1] != TUSS_DEVICE_ID:
        print("Unexpected response from device '%x', should be '%x'" %
              (rd[1], TUSS_DEVICE_ID))
        return -1

    ret = 0
    ret |= tuss_write_register(TUSS_REG_BPF_CONFIG_1, TUSS_BPF_CONFIG_1_RESET)
    ret |= tuss_write_register(TUSS_REG_BPF_CONFIG_2, TUSS_BPF_CONFIG_2_RESET)
    ret |= tuss_write_register(TUSS_REG_DEV_CTRL_1, TUSS_DEV_CTRL_1_RESET)
    ret |= tuss_write_register(TUSS_REG_DEV_CTRL_2,
                               TUSS_DEV_CTRL_2_LOGAMP_DIS_FIRST |
                               TUSS_DEV_CTRL_2_LOGAMP_DIS_LAST)
    ret |= tuss_write_register(TUSS_REG_DEV_CTRL_3, TUSS_DEV_CTRL_3_IO_MODE_1)
    ret |= tuss_write_register(TUSS_REG_VDRV_CTRL,
                               TUSS_VDRV_CTRL_VDRV_CURR_LVL_20MA |
                               TUSS_VDRV_CTRL_VDRV_VOLT_LVL_5V)
    ret |= tuss_write_register(TUSS_REG_ECHO_INT_CONFIG, TUSS_ECHO_INT_CONFIG_RESET)
    ret |= tuss_write_register(TUSS_REG_ZC_CONFIG, TUSS_ZC_CONFIG_RESET)
    ret |= tuss_write_register(TUSS_REG_BURST_PULSE, TUSS_BURST_PULSE_BURST_PULSE_16)
    ret |= tuss_write_register(TUSS_REG_TOF_CONFIG, TUSS_TOF_CONFIG_RESET)

    return ret

def tuss_burst():
    # Set clock for the burst frequency
    ft_set_clock(d, TUSS_BURST_FREQ)

    ret = ft_write(d,
             # SK high (see recommendation about the IO2 from TI), IO1 low
             (SET_BITS_LOW, SK_PIN|CS_PIN, OUT_PINS) +
             # Number of burst pulses in bytes
             ft_make_hdr(CLK_BYTES, TUSS_BURST_PULSE_BURST_PULSE_16//8) +
             # SK|CS|IO1 high, other low
             (SET_BITS_LOW, SK_PIN|CS_PIN|IO1_PIN, OUT_PINS))
    if ret != 9:
        return -1

    return 0

d = ftdi.Device()
d.ftdi_fn.ftdi_set_bitmode(0, 0); # reset
d.ftdi_fn.ftdi_set_bitmode(0, BITMODE_MPSSE)

# CS|IO1 high, other low
ft_write(d, (SET_BITS_LOW, CS_PIN|IO1_PIN, OUT_PINS))

ret = tuss_default_setup()
print("TUSS setup: %d" % ret)

if ret == 0:
    ret = tuss_burst()
    print("TUSS burst: %d" % ret)
