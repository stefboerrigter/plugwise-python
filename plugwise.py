import urllib2, base64, xmltodict, sys  #required packages
import xml.etree.ElementTree as ET      #also required

username = 'smile'            #username to login to the gateway
password = 'YOURKEY'          #the id of the gateway (8 letter password)
ipaddress = '192.168.188.46'  #Ip Address of Adam (smile) gateway
IPDOMOTICZ = '127.0.0.1'      #LocalHost in my case
debug = False

#wanted thermostats
Thermostats = {"LisaKeuken"}
#Mapping for devices to domoticz IDXes setPoint and temp
DeviceMapping = {"LisaKeuken": {"setPoint": 104, "temp":105}}

#####################################
#validate input arguments, only used to distinguish if debug printing is required
#####################################
def validateArguments(arguments):
    global debug
    for arg in arguments:
        if arg == "debug":
            debug = True

#####################################
# Print debug statements
#####################################
def debugPrint(str):
   if debug:
      print str

#####################################
#Obtain XML information from Adam and parse thermostat values
#####################################
def parsePlugwise():
    request = urllib2.Request('http://%s/core/appliances' % (ipaddress))
    base64string = base64.b64encode('%s:%s' % (username, password))
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)

    dataObject = dict()

    data = result.read()
    result.close()
 
    debugPrint( "Searching for thermostats: ")
    for thermostat in Thermostats:
         debugPrint(thermostat)
  
    debugPrint("-----------------------------------------")
    debugPrint("-----------------------------------------")
    
    devices = ET.fromstring(data)
    
    for appliance in devices.findall('appliance'):
        debugPrint("-----------------------------------------")
        name = appliance.find('name').text
        if name in Thermostats:
            debugPrint( "Wanted Thermostat Found [%s]" % name)
            temp = 0.0
            setPoint = 0.0
            logs = appliance.find('logs')
            for log in logs:
                #lastUpdate = log.find('updated_date').text
                #debugPrint("Last Update timestamp: %s " % lastUpdate)
                type = log.find('type').text
                period = log.find('period')
                #debugPrint("Start Date: %s, End Date: %s" % (period.get('start_date'), period.get('end_date')))
                measurement = period.find('measurement')
                updateDate = measurement.get('log_date')
                debugPrint("Update Timestamp: [%s]" % updateDate)
                if type == "thermostat":
                    debugPrint("Thermostat Setpoint: %s" % measurement.text)
                    setPoint = float(measurement.text)
                elif type == "temperature_offset":
                    debugPrint("Offset: %s" % measurement.text)
                elif type == "temperature":
                    debugPrint( "Temperature: %s " % measurement.text)
                    temp = float(measurement.text)
            dataObject[name] = {'temp': temp, 'setpoint':setPoint, 'update':updateDate}
                
        debugPrint("Name Object: " + name + ".")
        debugPrint(".....")
        debugPrint("") 


    debugPrint("-----------------------------------------")
    debugPrint("-----------------------------------------")
    return dataObject

#####################################
#Push parsed data to the domoticz server
#####################################
def uploadValueToDomoticz(dataObject):
    debugPrint (dataObject)
    debugPrint (DeviceMapping)
    for thermostat in dataObject:
	idxSetPoint = DeviceMapping[thermostat]["setPoint"]
	idxTemp = DeviceMapping[thermostat]["temp"]
        debugPrint("Thermostatobject: %s " % dataObject[thermostat])
        debugPrint ("http://%s:8080/json.htm?type=command&param=setsetpoint&idx=%s&setpoint=%f" % (IPDOMOTICZ, idxSetPoint, dataObject[thermostat]['setpoint']))
        urlStatus = urllib2.urlopen("http://%s:8080/json.htm?type=command&param=setsetpoint&idx=%s&setpoint=%f" % (IPDOMOTICZ, idxSetPoint, dataObject[thermostat]['setpoint']))
        debugPrint ("http://%s:8080/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%f" % (IPDOMOTICZ, idxTemp, dataObject[thermostat]['temp']))
        urlStatus = urllib2.urlopen("http://%s:8080/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%f" % (IPDOMOTICZ, idxTemp, dataObject[thermostat]['temp']))
 
        
########################################
######## "Main" steps to perform
#######################################

validateArguments(sys.argv)

uploadValueToDomoticz(parsePlugwise())

print "Done"
