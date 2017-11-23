/**
 * rego Adapter for CCU.IO
 *
 * Copyright (c) 11'2013 anli
 *
 * get values from ivt rego 600 series (especially Junkers TM75, IVT Rego 634 control unit)
 *
 * todo: werte direkt über den digi realport auslesen und steuerung ermöglichen
 */

var settings = require(__dirname+'/../../settings.js');

if (!settings.adapters.rego || !settings.adapters.rego.enabled) {
    process.exit();
}

var logger       = require(__dirname+'/../../logger.js');
var io           = require('socket.io-client');
var regoSettings = settings.adapters.rego.settings;

if (settings.ioListenPort) {
    var socket = io.connect("127.0.0.1", {
        port: settings.ioListenPort
    });
} else if (settings.ioListenPortSsl) {
    var socket = io.connect("127.0.0.1", {
        port: settings.ioListenPortSsl,
        secure: true
    });
} else {
    process.exit();
}

socket.on('connect', function () {
    logger.info("adapter rego  connected to ccu.io");
    initialize();
});

socket.on('disconnect', function () {
    logger.info("adapter rego  disconnected from ccu.io");
});

function initialize() {

    try {
        var dp = regoSettings.firstId + 1;

        socket.emit("setObject", dp, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1",
            TypeName: "CHANNEL",
            Address: "REGO600_" + regoSettings.firstId + ":1",
            HssType: "REGO600_STATUS",
            Parent: regoSettings.firstId,
            DPs: {
                RADIATOR_RETURN_TEMP_GT1: dp + 1,
                OUTDOOR_TEMP_GT2: dp + 2,
                HOT_WATER_TEMP_GT3: dp + 3,
                FORWARD_TEMP_GT4: dp + 4,
                ROOM_TEMP_GT5: dp + 5,
                COMPRESSOR_TEMP_GT6: dp + 6,
                HEAT_FLUID_OUT_TEMP_GT8: dp + 7,
                HEAT_FLUID_IN_TEMP_GT9: dp + 8,
                COLD_FLUID_IN_TEMP_GT10: dp + 9,
                COLD_FLUID_OUT_TEMP_GT11: dp + 10,
                EXTERNAL_HOT_WATER_GT3X: dp + 11,
                GROUND_LOOP_PUMP_P3: dp + 12,
                COMPRESSOR: dp + 13,
                ADDITIONAL_HEAT_3KW: dp + 14,
                ADDITIONAL_HEAT_6KW: dp + 15,
                RADIATOR_PUMP_P1: dp + 16,
                HEAT_CARRIER_PUMP_P2: dp + 17,
                THREE_WAY_VALVE_VXV: dp + 18,
                ALARM: dp + 19,
                GT1_TARGET_VALUE: dp + 20,
                GT1_ON_VALUE: dp + 21,
                GT1_OFF_VALUE: dp + 22,
                GT3_TARGET_VALUE: dp + 23,
                GT3_ON_VALUE: dp + 24,
                GT3_OFF_VALUE: dp + 25,
                GT4_TARGET_VALUE: dp + 26,
                ADD_HEAT_POWER_PERCENT: dp + 27,
                HEAT_CURVE: dp + 28,
                HEAT_CURVE_FINE_ADJUST: dp + 29,
                INDOOR_TEMP_SETTING: dp + 30,
                CURVE_INFLUENCE_BY_INDOOR_TEMP: dp + 31,
                ADJUST_CURVE_AT_20DEG_OUT: dp + 32,
                ADJUST_CURVE_AT_15DEG_OUT: dp + 33,
                ADJUST_CURVE_AT_10DEG_OUT: dp + 34,
                ADJUST_CURVE_AT_5DEG_OUT: dp + 35,
                ADJUST_CURVE_AT_0DEG_OUT: dp + 36,
                ADJUST_CURVE_AT_M5DEG_OUT: dp + 37,
                ADJUST_CURVE_AT_M10DEG_OUT: dp + 38,
                ADJUST_CURVE_AT_M15DEG_OUT: dp + 39,
                ADJUST_CURVE_AT_M20DEG_OUT: dp + 40,
                ADJUST_CURVE_AT_M25DEG_OUT: dp + 41,
                ADJUST_CURVE_AT_M30DEG_OUT: dp + 42,
                ADJUST_CURVE_AT_M35DEG_OUT: dp + 43,
                HEAT_CURVE_COUPLING_DIFF: dp + 44,
                ADD_HEAT_TIMER_SEC: dp + 45,
                DISPLAY_ROW1: dp + 46,
                DISPLAY_ROW2: dp + 47,
                DISPLAY_ROW3: dp + 48,
                DISPLAY_ROW4: dp + 49,
                LED1_POWER: dp + 50,
                LED2_PUMP: dp + 51,
                LED3_ADD_HEAT: dp + 52,
                LED4_BOILER: dp + 53,
                LED5_ALARM: dp + 54
            }
        });

        socket.emit("setObject", dp + 1, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.RADIATOR_RETURN_TEMP_GT1",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 2, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.OUTDOOR_TEMP_GT2",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 3, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HOT_WATER_TEMP_GT3",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 4, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.FORWARD_TEMP_GT4",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 5, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ROOM_TEMP_GT5",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 6, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.COMPRESSOR_TEMP_GT6",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 7, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_FLUID_OUT_TEMP_GT8",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 8, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_FLUID_IN_TEMP_GT9",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 9, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.COLD_FLUID_IN_TEMP_GT10",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 10, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.COLD_FLUID_OUT_TEMP_GT11",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 11, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.EXTERNAL_HOT_WATER_GT3X",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 12, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GROUND_LOOP_PUMP_P3",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 13, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.COMPRESSOR",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 14, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADDITIONAL_HEAT_3KW",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 15, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADDITIONAL_HEAT_6KW",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 16, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.RADIATOR_PUMP_P1",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 17, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_CARRIER_PUMP_P2",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 18, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.THREE_WAY_VALVE_VXV",
            TypeName: "HSSDP",
            ValueType: 16,
            Parent: dp
        });
        socket.emit("setObject", dp + 19, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ALARM",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 20, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT1_TARGET_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 21, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT1_ON_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 22, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT1_OFF_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 23, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT3_TARGET_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 24, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT3_ON_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 25, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT3_OFF_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 26, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.GT4_TARGET_VALUE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 27, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADD_HEAT_POWER_PERCENT",
            TypeName: "HSSDP",
            ValueType: 16,
            ValueUnit: "%",
            Parent: dp
        });
        socket.emit("setObject", dp + 28, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_CURVE",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 29, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_CURVE_FINE_ADJUST",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 30, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.INDOOR_TEMP_SETTING",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "°C",
            Parent: dp
        });
        socket.emit("setObject", dp + 31, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.CURVE_INFLUENCE_BY_INDOOR_TEMP",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 32, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_20DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 33, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_15DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 34, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_10DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 35, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_5DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 36, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_0DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 37, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M5DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 38, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M10DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 39, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M15DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 40, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M20DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 41, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M25DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 42, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M30DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 43, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADJUST_CURVE_AT_M35DEG_OUT",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 44, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.HEAT_CURVE_COUPLING_DIFF",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 45, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.ADD_HEAT_TIMER_SEC",
            TypeName: "HSSDP",
            ValueType: 4,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 46, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.DISPLAY_ROW1",
            TypeName: "HSSDP",
            ValueType: 20,
            "ValueSubType": 11,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 47, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.DISPLAY_ROW2",
            TypeName: "HSSDP",
            ValueType: 20,
            "ValueSubType": 11,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 48, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.DISPLAY_ROW3",
            TypeName: "HSSDP",
            ValueType: 20,
            "ValueSubType": 11,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 49, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.DISPLAY_ROW4",
            TypeName: "HSSDP",
            ValueType: 20,
            "ValueSubType": 11,
            ValueUnit: "",
            Parent: dp
        });
        socket.emit("setObject", dp + 50, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.LED1_POWER",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 51, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.LED2_PUMP",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 52, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.LED3_ADD_HEAT",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 53, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.LED4_BOILER",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });
        socket.emit("setObject", dp + 54, {
            Name: "REGO600.REGO600_" + regoSettings.firstId + ":1.LED5_ALARM",
            TypeName: "HSSDP",
            ValueType: 2,
            Parent: dp
        });

        socket.emit("setObject", regoSettings.firstId, {
            Name: "rego600series",
            TypeName: "DEVICE",
            HssType: "rego600",
            Address: "REGO600_" + regoSettings.firstId,
            Interface: "CCU.IO",
            Channels: [
                dp
            ]
        }, function() {
            socket.disconnect();
            logger.info("adapter rego  terminating");
            setTimeout(function () {
                process.exit();
            }, 1000);
        });
    }
    catch (exp) {
        logger.warn("adapter rego  ERROR " + exp);
    }
}

