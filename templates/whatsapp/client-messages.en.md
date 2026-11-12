# WhatsApp Client Message Templates (English)

For non-Arabic-speaking clients. Same 30 messages and order as `client-messages.md`.

## How to use
- Replace everything between `{{ }}` before sending. Company details come from `.claude/company/profile.md`.
- WhatsApp formatting: `*text*` shows bold, `_text_` shows italic.
- Only mention accreditations, licences or standards the company actually holds. Delete lines marked `[Optional: ...]` if they don't apply.

---

## General

### 1. Welcome and company introduction (first contact)
```
Hello {{client_name}},

This is {{employee_name}} from *{{company_name}}*.
Our services:
▫️ Installation and maintenance of *medical gas* pipeline systems (oxygen, medical air, vacuum, nitrous oxide, CO₂)
▫️ Installation and maintenance of *industrial and laboratory gas* systems (nitrogen, argon, helium, compressed air and more)
▫️ Preventive and corrective *laboratory equipment maintenance*
▫️ *Equipment calibration* with calibration certificates

How can we help you? Let me know what you need and I'll connect you with the right specialist.
📞 {{contact_number}}
```

### 2. Out-of-hours auto-reply
```
Thank you for contacting *{{company_name}}* 🙏
Our working hours: {{working_days}}, {{from_time}} to {{to_time}}.
We'll get back to you as soon as we're back.

🚨 For an *emergency* on a medical gas system or a critical device, please call our emergency line: {{emergency_number}}
```

### 3. Request received – information needed
```
Thank you {{client_name}}, we've received your request ✅
To prepare an accurate quotation, please send us:
1️⃣ Organisation name and city / site location
2️⃣ Service type: (installation / maintenance / calibration)
3️⃣ List of equipment or gas points (type, manufacturer, model, quantity)
4️⃣ Annual contract or a one-off visit?
5️⃣ Any drawings or photos available

You can send them right here 📎
```

### 4. Site survey booking
```
Hello {{client_name}},
Your *site survey* is confirmed ✅
📅 Date: {{date}}
⏰ Time: {{time}}
📍 Location: {{location}}
👷 Engineer: {{engineer_name}} – {{engineer_mobile}}

Please arrange site access, and if possible have a member of your team available.
If you need to reschedule, kindly let us know a day in advance 🙏
```

### 5. Sending the quotation
```
Hello {{client_name}},
Please find attached *Quotation No. {{quote_number}}* for: {{service_description}} 📄

▫️ Total: SAR {{amount}} {{incl./excl.}} VAT
▫️ Delivery period: {{duration}}
▫️ Valid for: {{validity}}

I'm happy to answer any questions or make adjustments. We look forward to working with you 🤝
```

### 6. Quotation follow-up (after 3–5 days)
```
Good afternoon {{client_name}},
Just following up on Quotation No. {{quote_number}} sent on {{date}}.
Do you have any comments, or would you like clarification on any item?
We can also arrange a short call or a site visit if that suits you.
```

### 7. Payment reminder (polite)
```
Dear {{client_name}},
A friendly reminder that Invoice No. *{{invoice_number}}* for SAR {{amount}} is due on {{due_date}}.
📎 A copy of the invoice is attached.
If payment has already been made, please share the transfer receipt. Thank you for your cooperation 🙏
```

### 8. Customer satisfaction survey
```
Thank you {{client_name}} for choosing *{{company_name}}* 🙏
Your feedback on our {{service_description}} matters to us:
⭐ On a scale of 1 to 5, how would you rate the service?
💬 What did you like most, and what could we do better?
```

---

## Medical Gases

### 9. Medical gas services introduction (hospitals, medical centres, clinics)
```
Dear {{client_name}},
*{{company_name}}* provides complete medical gas pipeline solutions:

🔹 Design and installation using cleaned-for-oxygen medical-grade copper pipe
🔹 Supply and installation of gas outlets, area alarm panels and zone valve boxes
🔹 Manifold rooms, medical air plants and vacuum plants
🔹 Testing and commissioning: pressure and leak testing, purging, purity testing and cross-connection checks
🔹 Preventive and emergency maintenance contracts

[Optional: We work to {{standards_we_follow}}]
[Optional: {{company licences / approvals with health authorities}}]

Would you like us to arrange a free site survey?
```

### 10. Medical gas preventive maintenance visit confirmation
```
Hello {{client_name}},
A reminder of the *medical gas system preventive maintenance* visit – {{facility_name}} 🏥
📅 {{date}} ⏰ {{time}}
👷 Team: {{technician_name}} – {{technician_mobile}}

The visit covers: manifolds and regulators, alarm panels, zone valve boxes, outlets, medical air compressors, vacuum pumps and leak checks.

⚠️ Some areas may need a short shutdown. We will coordinate with nursing and facility management beforehand, and no valve will be closed without your approval.
```

### 11. Emergency fault report received (medical gas)
```
Your report has been received 🚨
Ticket No.: *{{ticket_number}}*
Fault: {{fault_description}}
Location: {{department/floor}}

👷 Technician {{technician_name}} is on the way, estimated arrival in {{duration}}.
📞 Direct contact: {{technician_mobile}}

⚠️ Until we arrive: please do not dismantle or adjust any part of the system, and use backup cylinders according to your facility's procedures.
```

### 12. Installation and testing completed (handover)
```
Hello {{client_name}},
We are pleased to confirm *completion of the medical gas pipeline installation* at {{location}} ✅

Completed:
✔️ Pressure and leak testing
✔️ Purging
✔️ Cross-connection and gas identity checks at every outlet
✔️ Purity testing [Optional, as per contract]
✔️ Alarm panel commissioning and testing

📎 Test reports and handover certificate attached.
We suggest scheduling a short training session for your team on alarm panels and emergency shut-off valves.
```

### 13. Maintenance contract expiry and renewal
```
Dear {{client_name}},
The *{{system_type}}* maintenance contract No. {{contract_number}} expires on *{{expiry_date}}* 📅

To keep your service uninterrupted, we recommend renewing the contract.
📎 Renewal offer attached, including {{visit_count}} preventive visits + breakdown response within {{response_time}}.

We'd be glad to continue serving you for another year 🤝
```

---

## Industrial and Laboratory Gases

### 14. Industrial gas services introduction (factories, laboratories, workshops)
```
Dear {{client_name}},
*{{company_name}}* installs and maintains industrial and laboratory gas systems:

🔸 Gases: nitrogen, argon, oxygen, CO₂, helium, hydrogen, acetylene, compressed air and gas mixtures
🔸 Piping: stainless steel or copper, depending on the gas and the required purity
🔸 Cylinder manifolds, pressure regulators, isolation valves and gas leak detectors
🔸 Gas lines for analytical instruments and high-purity gas systems
🔸 Pressure and leak testing, commissioning and preventive maintenance

Send us your drawings or equipment list and we'll arrange a site survey and quotation.
```

### 15. Gas system maintenance visit report
```
Hello {{client_name}},
The maintenance visit for the gas system at {{location}} was completed on {{date}} ✅

📋 *Summary:*
▫️ Overall condition: {{good / action required}}
▫️ Leaks: {{none / number and location}}
▫️ Regulators and valves: {{condition}}
▫️ Work done on site: {{actions}}

⚠️ *Recommendations:* {{recommendations}}
📎 Full report attached.
```

### 16. Safety alert – leak detected
```
⚠️ *Safety alert – {{facility_name}}*
During inspection we found a *leak* on the {{gas_type}} line at {{location}}.

Action taken: {{line isolated / temporary repair}}
Required: {{permanent repair / part replacement}} – quotation to follow within {{duration}}.

Please do not reopen the isolated valve before coordinating with us.
Contact: {{engineer_name}} – {{engineer_mobile}}
```

---

## Laboratory Equipment Maintenance

### 17. Laboratory equipment maintenance introduction
```
Dear {{client_name}},
*{{company_name}}* specialises in laboratory equipment maintenance:

🔬 Analytical and measuring instruments, centrifuges, incubators and ovens, autoclaves, biosafety cabinets and fume hoods, balances, pH meters, laboratory refrigerators and freezers, and more
🛠️ Scheduled preventive maintenance + breakdown repairs
📦 Spare parts supply
📄 Technical report after every visit and a service history for each device

[Optional: Brands we service: {{brands}}]
[Optional: {{manufacturer authorisations, if any}}]

Could you send us your equipment list (type, manufacturer, model, quantity) so we can prepare an annual contract offer?
```

### 18. Preventive maintenance visit confirmation
```
Hello {{client_name}},
A reminder of the *laboratory equipment preventive maintenance* visit 🔬
📅 {{date}} ⏰ {{time}}
📍 {{lab/department}}
👷 Engineer: {{engineer_name}} – {{engineer_mobile}}

Equipment covered in this visit: {{device_count}} devices (list attached).
If possible, please switch off the listed equipment and remove any samples before the visit 🙏
```

### 19. Equipment fault report received
```
Your report has been logged ✅
🔖 Ticket No.: *{{ticket_number}}*
🔬 Device: {{device_type}} – {{manufacturer/model}} – Serial No. {{serial_number}}
⚠️ Fault: {{fault_description}}

⏱️ Visit scheduled: {{date_and_time}}
👷 Engineer: {{engineer_name}}

A photo or short video of the fault, or of any error message on the screen, will help us bring the likely spare parts 📸
```

### 20. Technician on the way
```
Hello {{client_name}} 👋
Our engineer *{{engineer_name}}* is on the way to you now 🚗
⏱️ Estimated arrival: {{time}}
📞 {{engineer_mobile}}
```

### 21. Repair completion report
```
Hello {{client_name}},
Ticket No. *{{ticket_number}}* has been completed ✅

🔬 Device: {{device_type}} – {{model}}
🔍 Cause of fault: {{root_cause}}
🛠️ Action taken: {{action}}
🔩 Parts replaced: {{parts / none}}
✔️ Current status: {{working normally / working with a remark}}

📎 Service report attached – please review and sign.
[Optional: We recommend {{calibrating the device after the repair}}, as the repair involved a part that affects measurement accuracy.]
```

### 22. Spare parts quotation
```
Hello {{client_name}},
Following inspection of the *{{device_type}} – {{model}}*, the following is required:
🔩 {{part_1}} — SAR {{price_1}}
🔩 {{part_2}} — SAR {{price_2}}
🛠️ Installation: SAR {{installation_cost}}

💰 Total: SAR {{total}} {{incl./excl.}} VAT
⏱️ Parts lead time: {{lead_time}}
🛡️ Parts warranty: {{warranty}}

We'll order the parts as soon as we receive your approval 🙏
```

### 23. Beyond economical repair / replacement recommended
```
Hello {{client_name}},
After technical inspection of the *{{device_type}} – Serial No. {{serial_number}}*, we found that:
▫️ {{reason: parts are no longer available from the manufacturer / repair cost exceeds {{percentage}}% of a new unit / the device is no longer supported by the manufacturer}}

We recommend {{replacement / decommissioning}} and are happy to propose suitable alternatives.
📎 Technical report attached.
```

---

## Calibration

### 24. Calibration services introduction
```
Dear {{client_name}},
*{{company_name}}* provides *equipment calibration* on site or at our laboratory:

⚖️ Balances and weights
🌡️ Temperature (incubators, ovens, refrigerators, water baths, autoclaves)
💧 Pipettes and volumetric glassware
🔄 Centrifuges (speed and time)
🧪 pH and conductivity meters
📏 Pressure, temperature and humidity gauges
[Add or remove according to our scope: {{calibration_scope}}]

📄 Each device receives a calibration certificate showing as-found and as-left results, measurement uncertainty and traceability to reference standards.
[Optional: Calibration is {{accredited by {{accreditation_body}} / performed through our accredited partner laboratory: {{lab_name}}}}]

Send us your equipment list and we'll share a quotation and an annual calibration plan 📋
```

### 25. Calibration due reminder (30 days before)
```
Dear {{client_name}},
Reminder: calibration of the following equipment expires within *30 days* 📅

{{equipment_list_and_due_dates}}
Example:
▫️ Analytical balance – Serial No. {{...}} – due {{date}}
▫️ Incubator – Serial No. {{...}} – due {{date}}

To keep you ready for audits and accreditation, we suggest booking your calibration now.
What date suits you?
```

### 26. Calibration appointment confirmation
```
Hello {{client_name}},
Your *calibration* appointment is confirmed ✅
📅 {{date}} ⏰ {{time}}
📍 {{location}}
🔢 Number of devices: {{quantity}}
👷 Technician: {{technician_name}}

📌 Before the visit, please:
▫️ Switch on temperature equipment (incubators, ovens) {{duration}} in advance so it stabilises
▫️ Clean the balances and keep them away from air-conditioning drafts and vibration
▫️ Have pipettes clean and ready
▫️ Have the quality or lab supervisor available to receive the results
```

### 27. Calibration certificates ready
```
Hello {{client_name}},
Calibration of your equipment is complete ✅
📄 *Calibration certificates* ({{quantity}} certificates) attached.

▫️ Within tolerance: {{pass_count}} devices
▫️ Adjusted, now within tolerance: {{adjusted_count}} devices
▫️ Out of tolerance: {{fail_count}} devices (details in the next message)

📅 Next calibration due: {{next_calibration_date}}
A calibration label has been placed on each device 🏷️
```

### 28. Device out of tolerance
```
⚠️ *Calibration result notice – {{lab_name}}*
Device: {{device_type}} – Serial No. {{serial_number}}
Result: *Out of tolerance* (deviation {{deviation}}, permitted limit {{tolerance}})
{{could not be adjusted on site / requires repair}}

📌 We recommend:
1️⃣ Stop using the device and tag it "Do not use"
2️⃣ Review results produced by the device since its last good calibration on {{last_calibration_date}}, as per your quality procedures
3️⃣ {{Repair and recalibrate / replace}} the device – quotation to follow within {{duration}}

For clarification: {{engineer_name}} – {{engineer_mobile}}
```

### 29. Annual calibration plan
```
Hello {{client_name}},
Please find attached the *{{year}} annual calibration and maintenance plan* for {{lab_name}} 📋

It includes:
▫️ A schedule of all equipment with calibration and maintenance due dates
▫️ Visits grouped into {{visit_count}} visits to minimise downtime
▫️ A reminder from us 30 days before each due date

Please review and approve it. We can adjust the dates to fit your schedule.
```

---

## Occasions
### 30. Seasonal greetings (Ramadan / Eid / Saudi National Day)
```
{{Ramadan Kareem / Eid Mubarak / Happy Saudi National Day 🇸🇦}}
Warm wishes from all of us at *{{company_name}}*.

📌 Our working hours during {{occasion}}: {{working_hours}}
[Optional: 🚨 Our emergency service is available 24/7: {{emergency_number}}]
```
