#!/usr/bin/env python
 
import urllib
import json
import os
 
from flask import Flask
from flask import request
from flask import make_response
import xml.etree.ElementTree as ET
import requests

HOST = "https://xmlpitest-ea.dhl.com"
API_URL = "/XMLShippingServlet"
 
# Flask app should start in global layout
app = Flask(__name__)
 
 
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
 
    print("Request:")
    print(json.dumps(req, indent=4))
 
    res = makeWebhookResult(req)
 
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
 
def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    track_id = parameters.get("track-id")
    xml_generate(track_id)
    response = do_request()
    print("Response:")
 
    return {
         "speech": response,
         "displayText": response,
         #"data": {},
         # "contextOut": [],
         "source": "apiai-onlinestore-shipping"
    }

def do_request():
    request = open("./output.xml", "r").read()
    print(request)
    url=HOST+API_URL
    req = requests.post(url, data=request, headers={'Content-Type': 'application/xml-www-form-urlencoded'})
    speech = process(req)
    return speech

def process(req):
    root = ET.fromstring(req.content)
    speech = "tracking information for AWB no:" + (root[1][0].text) + "\n"
    if root[1][1][0].text != 'success':
        specch += "No shipment data found\nPlease check your AWB number and try again"
        return
    speech += "Shippment information:\n"
    speech += "Shipment started at " + root[1][2][0][0].text +" " + root[1][2][0][1].text + "\n"
    speech += "Shipment ended at " + root[1][2][1][0].text +" " + root[1][2][1][1].text + "\n"
    speech += "Shippers name is " + root[1][2][2].text + "\n"
    speech += "Consignee name is " + root[1][2][4].text + "\n"
    speech += "Shipped on " + root[1][2][5].text + "\n"  
    return speech 
def xml_generate(track_id):
    tree = ET.parse('sample.xml')
    root = tree.getroot()
    siteID = 'DServiceVal'
    password = 'testServVal'
    message_time = '2003-06-25T11:28:56-08:00'
    message_reference = '1234567890123456789012345678'
    awb_number = track_id 
    root[0][0][0].text = message_time
    root[0][0][1].text = message_reference
    root[0][0][2].text = siteID
    root[0][0][3].text = password
    root[2].text = str(awb_number)	
    tree.write('output.xml')
 
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
 
    print("Starting app on port"+ str(port))
 
    app.run(debug=True, port=port, host='0.0.0.0')

