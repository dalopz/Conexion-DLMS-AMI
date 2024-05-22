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
from gurux_dlms.objects import GXDLMSObject, GXDLMSClock



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
        try:
            print("gurux_dlms version: " + pkg_resources.get_distribution("gurux_dlms").version)
            print("gurux_net version: " + pkg_resources.get_distribution("gurux_net").version)
            print("gurux_serial version: " + pkg_resources.get_distribution("gurux_serial").version)
        except Exception:
            #It's OK if this fails.
            print("pkg_resources not found")

        # args: the command line arguments
        reader = None
        settings = GXSettings()
        try:
            # //////////////////////////////////////
            #  Handle command line parameters.
            ret = settings.getParameters(args)
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
                        GXDLMSObjectCollection.extend(c)
                        if settings.client.objects:
                            read = True
                    except Exception:
                        read = False
                if not read:
                    reader.getAssociationView()
                for k, v in settings.readObjects:
                    obj = GXDLMSObjectCollection.findByLN(ObjectType.NONE, k)
                    if obj is None:
                        raise Exception("Unknown logical name:" + k)
                    if k == "1.1.72.7.0.255":
                        val = reader.read(obj, v)
                        print(val)
                    
                if settings.outputFile:
                    GXDLMSObjectCollection.save(settings.outputFile)
            else:
                
                print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                #reader.get_value_by_obis_code('1.1.72.7.0.255')
                RTC = GXDLMSClock("0.0.1.0.0.255")
                rtc_val = reader.read(RTC, 2)
                rtc_str = str(rtc_val) 
                #reader.read(GXDLMSObject('43744',None,0),3)
                #reader.get_value_by_obis_code('1.0.31.7.126.255')
                #reader.readAll(settings.outputFile)
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
            
    

if __name__ == '__main__':
   
    sampleclient.main(sys.argv)
