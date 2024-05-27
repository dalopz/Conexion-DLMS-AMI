#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
import os
import sys
import traceback
import time
import schedule
import requests
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


try:
    import pkg_resources
    #pylint: disable=broad-except
except Exception:
    #It's OK if this fails.
    print("pkg_resources not found")

#pylint: disable=too-few-public-methods,broad-except
class sampleclient():
    @classmethod
    def main(cls, args):
        # args: the command line arguments
        target_url = "http://localhost:1026/v2/entities/SM_EVI01/attrs"
        headers = {
            "Content-Type": "application/json"
        }
        def job():
            reader = None
            settings = GXSettings()
            try:
                # //////////////////////////////////////
                #  Handle command line parameters.
                argumentos = ['main.py', '-r', 'sn', '-c', '32', '-s', '1', '-h', '10.60.63.21', '-p', '4059', '-P', '00000000', '-a', 'Low']
                ret = settings.getParameters(argumentos)
                print(args)
                if ret != 0:
                    return
                # //////////////////////////////////////
                #  Initialize connection settings.
                if not isinstance(settings.media, (GXSerial, GXNet)):
                    raise Exception("Unknown media type.")
                # //////////////////////////////////////
                reader = GXDLMSReader(settings.client, settings.media, settings.trace, settings.invocationCounter)
                print('hizo el reader')
                settings.media.open()
                print('hizo el media.open')
                if settings.readObjects:
                    print('if settings')
                    read = False
                    reader.initializeConnection()
                    print('conectando')
                    
                    if settings.outputFile and os.path.exists(settings.outputFile):
                        try:
                            c = GXDLMSObjectCollection.load(settings.outputFile)
                            settings.client.objects.extend(c)
                            if settings.client.objects:
                                read = True
                        except Exception:
                            read = False
                    if not read:
                        reader.getAssociationView()
                    for k, v in settings.readObjects:
                        obj = settings.client.objects.findByLN(ObjectType.NONE, k)
                        if obj is None:
                            raise Exception("Unknown logical name:" + k)
                        val = reader.read(obj, v)
                        print(val)
                        reader.showValue(v, val)
                    if settings.outputFile:
                        settings.client.objects.save(settings.outputFile)
                else:   
                    reader.initialize_get_value_by_obis_code(settings.outputFile)
                    #reader.get_value_by_obis_code("1-1:4.9.2")  NO ENCONTRADO
                    
                    patch_payload = {
                        "activeenergyexport":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:2.8.0")
                        },
                        "activeenergyexportday":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:2.9.2")
                        },
                        "activeenergyimport":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:1.8.0")
                        },
                        "activeenergyimportday":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:1.9.2")
                        },
                        "activepower":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:16.7.0")
                        },
                        "activepower1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:36.7.0")
                        },
                        "activepower2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:56.7.0")
                        },
                        "activepower3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:76.7.0")
                        },
                        "frecuency":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:14.7.0")
                        },
                        "harmonicsi1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:31.7.126")
                        },
                        "harmonicsi2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:51.7.126")
                        },
                        "harmonicsi3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:71.7.126")
                        },
                        "harmonicsv1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:32.7.126")
                        },
                        "harmonicsv2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:52.7.126")
                        },
                        "harmonicsv3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:72.7.126")
                        },
                        "i1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:31.7.0")
                        },
                        "i1angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.4")
                        },
                        "i2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:51.7.0")
                        },
                        "i2angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.5")
                        },
                        "i3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:71.7.0")
                        },
                        "i3angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.6")
                        },
                        "in":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:91.7.0")
                        },
                        "powerfactor1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:33.7.0")
                        },
                        "powerfactor2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:53.7.0")
                        },
                        "powerfactor3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:73.7.0")
                        },
                        "reactiveenergyexport":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:4.8.0")
                        },
                        "reactiveenergyexportday":{
                            "type": "Number",
                            "value": 0
                        },
                        "reactiveenergyimport":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:3.8.0")
                        },
                        "reactiveenergyimportday":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:3.9.2")
                        },
                        "reactivepower":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:131.7.0")
                        },
                        "reactivepower1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:151.7.0")
                        },
                        "reactivepower2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:171.7.0")
                        },
                        "reactivepower3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-4:191.7.0")
                        },
                        "relativethdcurrent":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:11.7.127")
                        },
                        "relativethdpower":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:15.7.127")
                        },
                        "relativethdvoltage":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-0:12.7.127")
                        },
                        "relativethdfactor":{
                            "type": "Number",
                            "value": 0
                        },
                        "totalpowerfactor":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:13.7.0")
                        },
                        "v1":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:32.7.0")
                        },
                        "v1angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.0")
                        },
                        "v1_ps":{
                            "type": "Number",
                            "value": 0
                        },
                        "v2":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:52.7.0")
                        },
                        "v2angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.1")
                        },
                        "v2_ps":{
                            "type": "Number",
                            "value": 0
                        },
                        "v3":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:72.7.0")
                        },
                        "v3angle":{
                            "type": "Number",
                            "value": reader.get_value_by_obis_code("1-1:81.7.2")
                        },
                        "v3_ps":{
                            "type": "Number",
                            "value": 0
                        }
                    }
                    response = requests.patch(target_url, headers=headers, json=patch_payload)
                    if response.status_code == 204:
                        print("Attributes updated successfully")
                    else:
                        print("Error updating attributes:", response.status_code)
                    print('else')
            except (ValueError, GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError) as ex:
                print(f'error:{ex}')
            except (KeyboardInterrupt, SystemExit, Exception) as ex:
                traceback.print_exc()
                if settings.media:
                    settings.media.close()
                reader = None
            finally:
                if reader:
                    try:
                        reader.close()
                    except Exception:
                        traceback.print_exc()
                print("Ended. Press any key to continue.")
                time.sleep(5)

        schedule.every(5).seconds.do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(2)
            
        

if __name__ == '__main__':
   
    sampleclient.main(sys.argv)
