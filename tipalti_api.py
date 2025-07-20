import requests
import hmac
import hashlib
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


class TipaltiAPI:
    """Simple Tipalti SOAP API client for user management"""
    
    def __init__(self, payer_name: str, master_key: str, is_sandbox: bool = True):
        self.payer_name = payer_name
        self.master_key = master_key
        self.is_sandbox = is_sandbox
        
        # Set API endpoint based on environment
        if is_sandbox:
            self.base_url = "https://api.sandbox.tipalti.com/v14/PayeeFunctions.asmx"
        else:
            self.base_url = "https://api.tipalti.com/v14/PayeeFunctions.asmx"
    
    def generate_signature(self, idap: str = "", additional_param: str = "") -> tuple:
        """Generate HMAC-SHA256 signature for API authentication"""
        timestamp = str(int(time.time()))
        signature_string = f"{self.payer_name}{idap}{additional_param}{timestamp}"
        
        signature = hmac.new(
            self.master_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return timestamp, signature
    
    def _make_soap_request(self, action: str, soap_body: str) -> str:
        """Make SOAP request to Tipalti API"""
        soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <{action} xmlns="http://Tipalti.org/">
      {soap_body}
    </{action}>
  </soap12:Body>
</soap12:Envelope>"""
        
        headers = {
            'Content-Type': f'application/soap+xml; charset=utf-8; action="http://Tipalti.org/{action}"'
        }
        
        try:
            response = requests.post(self.base_url, data=soap_envelope, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            raise
    
    def get_payees_list(self) -> List[Dict]:
        """Get list of all payees from Tipalti"""
        timestamp, signature = self.generate_signature()
        
        soap_body = f"""
      <payerName>{self.payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>"""
        
        try:
            # Try GetExtendedPayeeDetailList method as found in documentation
            response_xml = self._make_soap_request('GetExtendedPayeeDetailList', soap_body)
            return self._parse_payees_list(response_xml)
        except Exception as e:
            print(f"Failed to get payees list: {e}")
            return []
    
    def get_payee_details(self, idap: str) -> Optional[Dict]:
        """Get detailed information for a specific payee"""
        timestamp, signature = self.generate_signature(idap)
        
        soap_body = f"""
      <payerName>{self.payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
      <idap>{idap}</idap>"""
        
        try:
            response_xml = self._make_soap_request('GetExtendedPayeeDetails', soap_body)
            return self._parse_payee_details(response_xml)
        except Exception as e:
            print(f"Failed to get payee details for {idap}: {e}")
            return None
    
    def deactivate_payee(self, idap: str) -> bool:
        """Deactivate a payee"""
        timestamp, signature = self.generate_signature(idap)
        
        soap_body = f"""
      <payerName>{self.payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
      <idap>{idap}</idap>
      <overrideMode>Override</overrideMode>
      <payeeInfo>
        <idap>{idap}</idap>
        <isActive>false</isActive>
      </payeeInfo>"""
        
        try:
            response_xml = self._make_soap_request('UpdateOrCreatePayeeInfo', soap_body)
            return self._parse_update_response(response_xml)
        except Exception as e:
            print(f"Failed to deactivate payee {idap}: {e}")
            return False
    
    def _parse_payees_list(self, xml_response: str) -> List[Dict]:
        """Parse GetPayeesList XML response"""
        try:
            root = ET.fromstring(xml_response)
            payees = []
            
            # Navigate to the payees data (namespace handling)
            for payee_elem in root.iter():
                if payee_elem.tag.endswith('PayeeInfo'):
                    payee_data = {}
                    for child in payee_elem:
                        tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        payee_data[tag_name] = child.text if child.text else ""
                    
                    if payee_data:  # Only add if we found data
                        payees.append(payee_data)
            
            return payees
        except ET.ParseError as e:
            print(f"Failed to parse payees list XML: {e}")
            return []
    
    def _parse_payee_details(self, xml_response: str) -> Optional[Dict]:
        """Parse GetExtendedPayeeDetails XML response"""
        try:
            root = ET.fromstring(xml_response)
            details = {}
            
            # Extract payee details from XML
            for elem in root.iter():
                if elem.text and not elem.tag.endswith('Response'):
                    tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    details[tag_name] = elem.text
            
            return details if details else None
        except ET.ParseError as e:
            print(f"Failed to parse payee details XML: {e}")
            return None
    
    def _parse_update_response(self, xml_response: str) -> bool:
        """Parse UpdateOrCreatePayeeInfo XML response"""
        try:
            root = ET.fromstring(xml_response)
            
            # Look for success indicators in the response
            for elem in root.iter():
                if 'result' in elem.tag.lower() or 'success' in elem.tag.lower():
                    if elem.text:
                        return elem.text.lower() in ['true', 'success', 'ok']
            
            # If no explicit success/failure, assume success if no error found
            for elem in root.iter():
                if 'error' in elem.tag.lower() or 'fault' in elem.tag.lower():
                    return False
            
            return True
        except ET.ParseError as e:
            print(f"Failed to parse update response XML: {e}")
            return False 