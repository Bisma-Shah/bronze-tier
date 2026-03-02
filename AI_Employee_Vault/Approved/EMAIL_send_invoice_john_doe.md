---
type: approval_request
action: send_email
to: john.doe@example.com
subject: Invoice #2026-001 - January Consulting Services
amount: 6000.00
created: 2026-02-24T10:30:00Z
expires: 2026-02-25T10:30:00Z
status: pending
---

# Approval Required: Send Invoice Email

## Action Details

- **Action Type**: Send Email
- **Recipient**: john.doe@example.com
- **Subject**: Invoice #2026-001 - January Consulting Services
- **Amount**: $6,000.00

## Invoice Summary

| Item | Details |
|------|---------|
| Service Period | January 1-31, 2026 |
| Hours | 40 hours |
| Rate | $150/hour |
| Total | $6,000.00 |
| Due Date | Net 30 (March 26, 2026) |

## Email Body (Draft)

```
Dear John,

Thank you for your business. Please find attached the invoice for consulting services provided in January 2026.

Invoice Number: #2026-001
Amount Due: $6,000.00
Due Date: March 26, 2026

If you have any questions, please don't hesitate to reach out.

Best regards,
Your AI Employee
```

## Attachment

- `/AI_Employee_Vault/Invoices/2026-001_John_Doe.pdf`

---

## How to Respond

### To Approve
Move this file to the `/Approved` folder. The system will automatically send the email.

### To Reject
Move this file to the `/Rejected` folder and add a note explaining why.

### To Modify
Edit this file with your changes, then move to `/Approved`.

---
*Created by AI Employee v0.1*
*Requires human approval before sending*
