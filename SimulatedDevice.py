import random
import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# replace with your device connection string (NOT IoT Hub connection string)
# (use primary first, if not working use secondary)
CONNECTION_STRING   = "<use_your_device_connection_string>"
PROTOCOL            = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT     = 10000
AVG_TEMPERATURE     = 25.2  # in Celcius
AVG_HUMIDITY        = 0.7   # 70%
SEND_CALLBACKS      = 0
MSG_TXT             = "{\"deviceId\": \"DummyDHTSensor_Demo\", \"temperature\": %.2f, \"humidity\": %.2f}"

def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print("Confirmation[%d] received for message with result = %s" % (user_context, result))
    map_properties = message.properties()
    print("- message id     : %s" % message.message_id)
    print("- correlation id : %s" % message.correlation_id)
    key_value_pair = map_properties.get_internals()
    print("- properties     : %s" % key_value_pair)
    SEND_CALLBACKS += 1
    print("Total calls confirmed: %d" % SEND_CALLBACKS)

def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    client.set_option("logtrace", 0)
    client.set_option("product_info", "DummyDHTSensor_Demo")
    return client

def iothub_client_telemetry_sample_run():
    try:
        client = iothub_client_init()
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit")
        message_counter = 0

        while True:
            rand_temperature    = AVG_TEMPERATURE + (random.random() * 1 - 1)
            rand_humidity       = AVG_HUMIDITY + (random.random())
            msg_txt_formatted   = MSG_TXT % (rand_temperature, rand_humidity)

            # messages can be encoded as string or bytearray
            if (message_counter & 1) == 1:
                message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
            else:
                message = IoTHubMessage(msg_txt_formatted)

            # optional: assign ids
            message.message_id      = "message_%d" % message_counter
            message.correlation_id  = "correlation_%d" % message_counter

            # optional: assign properties
            prop_map  = message.properties()
            prop_text = "PropMsg_%d" % message_counter
            prop_map.add("Property", prop_text)

            client.send_event_async(message, send_confirmation_callback, message_counter)
            print("IoTHubClient.send_event_async accepted message " + 
                  "[%d] for transmission to IoT Hub" % message_counter)
            
            status = client.get_send_status()
            print("Send status: %s" % status)
            time.sleep(30) # 30 seconds

            status = client.get_send_status()
            print("Send status: %s" % status)

            message_counter += 1
    except IoTHubError as iothub_error:
        print("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

if __name__ == '__main__':
    print("Simulating a device using the Azure IoT Hub Device SDK for Python")
    print("- Protocol: %s" % PROTOCOL)
    print("- Connection string: %s" % CONNECTION_STRING)
    iothub_client_telemetry_sample_run()
