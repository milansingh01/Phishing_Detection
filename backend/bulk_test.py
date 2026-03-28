import requests
import json

# Your big list of emails goes here
emails = [
{"email_id":"H001","subject":"Re: Account access follow-up [Ref:8821]","email_body":"Dear Customer,\n\nWe noticed a retry attempt on your account (Ref:8821).\nIf this was you, no action required.\n\nअगर यह आपने नहीं किया, you may review session details below:\nhttp://secure-bank-login.xyz\n\nAttachment: session_log_8821.pdf\n\n--\nSecurity Ops\n(This is an automated message)"},

{"email_id":"H002","subject":"Txn Update // ID:AX9912","email_body":"Estimado cliente,\n\nYour recent debit (₹4,820) is processed.\nIf discrepancy exists, please refer attached.\n\nAdjunto: txn_details_AX9912.pdf\n\nGracias,\nBanking Team"},

{"email_id":"H003","subject":"Document Re-validation Required","email_body":"Hello,\n\nYour KYC document requires re-validation due to format mismatch.\n\nकृपया updated copy upload करें or confirm via portal:\nhttp://secure-bank-login.xyz\n\nAttachment: kyc_form.zip\n\nRegards"},

{"email_id":"H004","subject":"Monthly Statement (Auto-generated)","email_body":"Dear user,\n\nYour monthly statement is attached.\n\nNote: कुछ entries pending reconciliation.\n\nAttachment: statement_march.pdf\n\n-- Bank"},

{"email_id":"H005","subject":"Login Attempt Notification","email_body":"Bonjour,\n\nUne tentative de connexion a été détectée.\nIf not recognized, please confirm session activity.\n\nhttp://secure-bank-login.xyz\n\n-- Sécurité"},

{"email_id":"H006","subject":"Service Update [Ticket#7712]","email_body":"Dear Customer,\n\nScheduled update completed.\nकुछ users may still experience delay.\n\nNo action needed.\n\n-- Ops Team"},

{"email_id":"H007","subject":"Pending Refund Case","email_body":"Hello,\n\nYour refund request is pending due to incomplete details.\n\nBitte prüfen Sie die Angaben:\nhttp://secure-bank-login.xyz\n\nAttachment: refund_case_771.zip"},

{"email_id":"H008","subject":"Alert: Profile sync issue","email_body":"Dear user,\n\nProfile sync failed at 03:21 AM.\n\nIf already resolved ignore.\nElse you may retry via secure endpoint.\n\nhttp://secure-bank-login.xyz\n\n-- Tech Team"},

{"email_id":"H009","subject":"Payment Received ✔","email_body":"Dear customer,\n\n₹6,200 credited.\n\nधन्यवाद for banking.\n\n-- Bank"},

{"email_id":"H010","subject":"Verification Reminder (soft notice)","email_body":"Hi,\n\nThis is a reminder regarding pending verification.\n\nNo immediate urgency, however services may be limited.\n\nआप चाहें तो यहाँ check कर सकते हैं:\nhttp://secure-bank-login.xyz\n\n-- Support"},

{"email_id":"H011","subject":"Re: Statement Access Issue","email_body":"Hola,\n\nWe received your query.\nStatement attached below.\n\nAdjunto: estado_cuenta.pdf\n\nGracias"},

{"email_id":"H012","subject":"Security Review Completed","email_body":"Dear client,\n\nNo suspicious activity detected.\n\nDanke for your cooperation.\n\n-- Bank Security"},

{"email_id":"H013","subject":"Account Limitation Notice","email_body":"Hello,\n\nSome features temporarily restricted.\n\nTo restore, minimal verification required.\n\nhttp://secure-bank-login.xyz\n\nRef: LIM-882"},

{"email_id":"H014","subject":"Internal: Ops Follow-up","email_body":"Team,\n\nUser reported mismatch in txn logs.\nAttached raw logs.\n\nAttachment: logs_8821.zip\n\n-- Internal Banking"},

{"email_id":"H015","subject":"Auto Notification: Device Change","email_body":"Dear user,\n\nDevice change detected.\nIf expected, ignore.\n\nElse review activity.\n\n-- Bank"},

{"email_id":"H016","subject":"KYC Sync Update","email_body":"Hello,\n\nKYC synced successfully.\nकुछ fields pending but not critical.\n\n-- Compliance"},

{"email_id":"H017","subject":"Follow-up Required","email_body":"Dear customer,\n\nWe tried contacting regarding your account.\n\nYou may respond or review here:\nhttp://secure-bank-login.xyz\n\n-- Support Desk"},

{"email_id":"H018","subject":"Debit Alert","email_body":"₹1,920 debited.\n\nIf this looks unusual, contact support.\n\nGracias"},

{"email_id":"H019","subject":"Reminder: Document Upload","email_body":"Hi,\n\nPending document not received.\n\nUpload optional but recommended.\n\nhttp://secure-bank-login.xyz\n\nAttachment: doc_upload.html"},

{"email_id":"H020","subject":"System Maintenance Log","email_body":"Scheduled maintenance completed.\n\nकुछ background jobs pending.\n\n-- System"},

{"email_id":"H021","subject":"Secure Document Access (Encrypted)","email_body":"Dear Customer,\n\nYour statement is encrypted for security.\n\nAccess using secure viewer:\nhttp://secure-bank-login.xyz\n\nAttachment: secure_viewer.zip\n\n-- Bank"},

{"email_id":"H022","subject":"Re: Payment Issue Follow-up","email_body":"Hi,\n\nWe checked your concern.\nNo issue found.\n\nIf still facing issue, you may retry login.\n\n-- Support"},

{"email_id":"H023","subject":"Account Review Completed","email_body":"Dear user,\n\nYour account review is complete.\n\nBitte überprüfen Sie details online:\nhttp://secure-bank-login.xyz\n\n-- Compliance"},

{"email_id":"H024","subject":"Statement Access Delay","email_body":"Dear Customer,\n\nWe are experiencing delay in statement generation.\n\nMeanwhile you may download temporary copy from portal.\n\n-- Bank"},

{"email_id":"H025","subject":"Security Certificate Update","email_body":"Dear user,\n\nDue to recent upgrade, certificate mismatch may occur.\n\nYou may re-login here:\nhttp://secure-bank-login.xyz\n\n-- Security"},

{"email_id":"H026","subject":"Transaction Dispute Update","email_body":"Hello,\n\nYour dispute case has been resolved.\n\nAttachment: dispute_report.pdf\n\n-- Bank"},

{"email_id":"H027","subject":"Auto Sync Failure Notice","email_body":"Hi,\n\nAuto sync failed.\n\nNo action required unless issue persists.\n\n-- System"},

{"email_id":"H028","subject":"KYC Reminder (Soft)","email_body":"Dear Customer,\n\nYour KYC is pending but not urgent.\n\nYou can update anytime via portal.\n\n-- Bank"},

{"email_id":"H029","subject":"Updated Terms (Action Recommended)","email_body":"Dear user,\n\nWe updated our policies.\n\nReview recommended:\nhttp://secure-bank-login.xyz\n\n-- Legal"},

{"email_id":"H030","subject":"Re: Login Issue","email_body":"Hola,\n\nWe resolved your login issue.\n\nIf still facing, retry.\n\nGracias"},

{"email_id":"H031","subject":"Internal Audit Request","email_body":"Team,\n\nPlease verify sample accounts for audit.\n\nUse internal dashboard.\n\n-- Audit"},

{"email_id":"H032","subject":"Payment Confirmation","email_body":"₹8,100 credited.\n\nDanke.\n\n-- Bank"},

{"email_id":"H033","subject":"Account Sync Required","email_body":"Dear user,\n\nSome services may not work until sync.\n\nContinue here:\nhttp://secure-bank-login.xyz\n\n-- Tech"},

{"email_id":"H034","subject":"Attachment Delivery Failure","email_body":"Dear Customer,\n\nYour document failed to deliver.\n\nDownload again from:\nhttp://secure-bank-login.xyz\n\n-- Mailer"},

{"email_id":"H035","subject":"Device Registration Complete","email_body":"Dear user,\n\nYour device is registered successfully.\n\nNo further action required.\n\n-- Bank"},

{"email_id":"H036","subject":"Refund Confirmation","email_body":"Dear customer,\n\nYour refund has been processed.\n\nAttachment: refund_receipt.pdf\n\n-- Bank"},

{"email_id":"H037","subject":"Profile Verification Notice","email_body":"Dear user,\n\nWe periodically review accounts.\n\nYou may ignore if recently verified.\n\nElse confirm:\nhttp://secure-bank-login.xyz\n\n-- Bank"},

{"email_id":"H038","subject":"Maintenance Completion","email_body":"Maintenance completed successfully.\n\nकुछ services delayed.\n\n-- System"},

{"email_id":"H039","subject":"Secure Message Received","email_body":"Dear user,\n\nYou have received a secure message.\n\nOpen securely:\nhttp://secure-bank-login.xyz\n\nAttachment: message.html"},

{"email_id":"H040","subject":"Balance Notification","email_body":"₹2,300 remaining.\n\nGracias.\n\n-- Bank"}
]

url = "http://127.0.0.1:8000/api/analyze"

print(f"Starting bulk test of {len(emails)} emails...")

for email in emails:
    payload = {
        "subject": email["subject"],
        "body": email["email_body"],
        "sender": email["email_id"]
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"✅ Processed {email['email_id']}: {response.json().get('status')}")
    else:
        print(f"❌ Failed {email['email_id']}: {response.status_code}")

print("Bulk test complete! Check your AlertShield Dashboard.")