# Email to Tipalti Support

**To:** support@tipalti.com  
**Subject:** IP Whitelist Not Working for SOAP API - Payer "Uplify" - URGENT

---

Dear Tipalti Support Team,

I am experiencing an issue with IP whitelisting for SOAP API access for payer **"Uplify"**.

## Issue Description
Despite correctly configuring the IP whitelist in the Tipalti dashboard, I continue to receive `InvalidPayerIpAddress` errors when making SOAP API calls.

## Configuration Details
- **Payer Name:** Uplify
- **IP Address:** 84.115.224.136
- **API Type:** SOAP API (PayeeFunctions.asmx)
- **Environment:** Production
- **Endpoint:** https://api.tipalti.com/v14/PayeeFunctions.asmx

## Dashboard Configuration
I have correctly configured the IP whitelist in the Tipalti dashboard:
- Source type: **API**
- Status: **Active** ✅
- Description: Local laptop for backup API calls
- Address type: **DNS IP/Host**
- Number: **84.115.224.136**

## Timeline
- IP added to whitelist: ~14:30 (over 1 hour ago)
- Issue persists: Still receiving InvalidPayerIpAddress error
- Multiple endpoints tested: All return same error

## API Call Details
- Method: GetPayeeDetails
- Error: InvalidPayerIpAddress
- Test Payee IDs: 37617, 37620, 18827 (known valid payees)
- Authentication: HMAC-SHA256 signature (working correctly)

## Technical Details
```
SOAP Endpoint: https://api.tipalti.com/v14/PayeeFunctions.asmx
HTTP Status: 200
SOAP Response Error: InvalidPayerIpAddress
Current IP: 84.115.224.136
```

## Request for Support
Please help investigate:
1. **Verify IP whitelist** is properly applied for SOAP API access
2. **Check if additional permissions** are needed for payer "Uplify"
3. **Review system logs** for IP 84.115.224.136 requests
4. **Confirm if SOAP API** has different whitelist requirements
5. **Any caching issues** that might delay whitelist activation

## Business Impact
This is blocking our ability to backup **3,857 active payees** from the system, which is critical for our operations.

## Additional Information
- We have working credentials (authentication succeeds)
- We can see the payees in the Tipalti dashboard
- Only the IP restriction is blocking API access
- All other connectivity tests pass

Please prioritize this issue as it's blocking critical backup operations.

Thank you for your assistance.

Best regards,
[Your Name]
[Your Contact Information]
[Company Name] 