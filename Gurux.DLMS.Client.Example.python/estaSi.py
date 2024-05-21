# ---------------------------------------------------------------------------
import os
import socket
import sys
import time
import traceback
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from gurux_dlms.objects.GXDLMSObjectCollection import GXDLMSObjectCollection
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
from gurux_dlms.GXDLMSClient import GXDLMSClient
from gurux_common.GXCommon import GXCommon
from gurux_dlms.enums.DataType import DataType
import locale
from gurux_dlms.GXDateTime import GXDateTime
from gurux_dlms.internal._GXCommon import _GXCommon
from gurux_dlms import GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError, GXDLMSTranslator
from gurux_dlms import GXByteBuffer, GXDLMSTranslatorMessage, GXReplyData
from gurux_dlms.enums import RequestTypes, Security, InterfaceType
from gurux_dlms.secure.GXDLMSSecureClient import GXDLMSSecureClient
from gurux_dlms.objects import GXDLMSObject

class Settings:
    def __init__(self):
        self.media = GXNet()
        self.trace = 'Info'
        self.client = GXDLMSClient(True)
        self.reader = None


def read_value(smart_meter):
    settings = Settings()
    with settings.media.SyncRoot:
        try:
            settings.media.Protocol = 'Tcp'
            settings.media.Port = smart_meter.Port
            settings.media.HostName = smart_meter.IP

            settings.client.Password = smart_meter.Password.encode('ascii')
            settings.client.ServerAddress = 1
            settings.client.ClientAddress = 32
            settings.client.Authentication = 'Low'
            settings.client.InterfaceType = 'HDLC'
            settings.client.UseLogicalNameReferencing = False

            settings.reader = GXDLMSReader(settings.client, settings.media, settings.trace)

            settings.media.Open()

            # Algunos medidores necesitan una pausa aquí
            time.sleep(1)
            settings.reader.InitializeConnection()

            for variable in smart_meter.Variables.values():
                if variable.Registry:
                    out_value = 0.0
                    settings.reader.GetValueByObisCode(variable.Registry, out_value)
                    variable.LastValue = out_value
                else:
                    variable.LastValue = (smart_meter.Variables[variable.Key[:2]].LastValue *
                                          smart_meter.HighVoltage / smart_meter.LowVoltage)

            smart_meter.TimeStamp = time.time()
            smart_meter.StatusType = 'Normal'
            settings.media.Close()

            ##epoch_time = DataSource.ConvertDateTimeToUnixEpoch(time.time())
            for variable in smart_meter.Variables.values():
                collection = f"{smart_meter.Name}_{variable.Name}"
                ##DataSource.InsertDocumentMongoDB(collection, variable.LastValue, epoch_time)

            values = {var.Name: var.LastValue for var in smart_meter.Variables.values()}
            ##DataSource.InsertDocumentInfluxDBLocal(smart_meter.Name, values, epoch_time)
            ##DataSource.InsertTopicKafka(smart_meter.Name, values, epoch_time)

            settings.reader.Close()

        except Exception as ex:
            smart_meter.StatusType = 'NotNormal'
            print(f"Meter NOT read {smart_meter.Name}")
            message = f"Meter not read {smart_meter.Name}. {str(ex)}"
            # Logging.Logger.Logging(message, EventLogEntryType.Error, Logging.Logger.LoggerEventID.SmartMeter)
            try:
                with socket.create_connection((smart_meter.IP, smart_meter.Port), timeout=10) as sock:
                    sock.close()
            except Exception:
                pass
        finally:
            if settings.reader is not None:
                settings.reader.Close()