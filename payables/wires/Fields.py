"""Fields for use in constructing a wire payment completely from scratch,
without use of a template in JPM Access.
"""

header_fields = [
    ["HEADER", 7],  # = 'HEADER'
    ["File Timestamp", 14],  # = 'YYYYMMDDHHMMSS'
    ["Version", 5],  # 5 including decimal indicator
]

trailer_fields = [
    ["TRAILER", 7],  # = 'TRAILER'
    ["Total Number of Records", 23],
    ["Hash Total Amount", 17],  # sum of all trx in file
]


record_fields = [["Input Type", 2]]
trx_fields = [
    # Transaction Information
    ["Method", 7],
    ["Debit Bank ID", 11],  # direct_input
    ["Account Number", 34],  # direct_input
    ["Bank-to-Bank Transfer", 1],
    ["Currency", 3],
    ["Payment Amount", 20],  # direct_input
    ["Equivalent Amount", 20],
    ["Clearing", 1],
    ["Beneficiary Residence", 1],
    ["Rate Type", 1],
    ["", 0],
]
vd_fields = [
    # Value Date Section
    ["Value Date", 8]  # direct_input #mm/dd/yyy
]

beneficiary_fields = [
    # Beneficiary Section
    ["ID Type", 34],  # = 'Account Number' | 'IBAN'
    ["ID Value", 34],
    ["Name", 35],  # direct_input
    ["Address 1", 35],
    ["Address 2", 35],
    ["Address 3", 32],
    ["City, State, Postal Code", 0],
    ["Country", 2],  # = 'US' | 'IN' | 'KY' (Cayman Islands) | 'GB' | 'ES'
    ["Supplementary ID Type", 34],
]

ben_bank_fields = [
    # Beneficiary Bank Section
    ["Supplementary ID Value", 34],  # = ''
    ["ID Type", 34],  # = 'United States Fed ABA' | 'Swift ID'
    ["ID Value", 34],
    ["Name", 35],
    ["Address 1", 35],
    ["Address 2", 35],
    ["Address 3", 32],
    ["Country", 2],  # = 'US' | 'IN' | 'KY' (Cayman Islands) | 'GB' | 'ES'
    ["Supplementary ID Type", 34],  # = 'No ID'
    ["Supplementary ID Value", 34],
]
unused_1 = [
    # Unused
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
]

int_bank_fields = [
    # Intermediary ID Section
    ["ID Type", 34],  # = 'Swift ID' | 'CHIPS Participant Number' |
    ["ID Value", 34],
    ["Name", 35],
    ["Address 1", 35],
    ["Address 2", 35],
    ["Address 3", 32],
    ["Country", 2],  # = 'US'
    ["Supplementary ID Type", 34],
    ["Supplementary ID Value", 34],
]

obo_fields = [
    # On Behalf Of Section
    ["ID Type", 0],  # = ''
    ["ID Value", 0],  # = ''
    ["Name", 0],  # = ''
    ["Address 1", 0],  # = ''
    ["Address 2", 0],  # = ''
    ["Address 3", 0],  # = ''
    ["Country", 2],  # = ''
]

unused_2 = [
    # Unused
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
]

trx_det_fields = [
    # Transaction Details Section
    ["Reference Sent with Payment", 16],  # = ''
    ["Internal Reference", 16],  # = ''
    ["On Behalf Of", 30],  # = ''
    ["Detail 1", 35],
    ["Detail 2", 35],
    ["Detail 3", 35],
    ["Detail 4", 35],
]

unused_3 = [
    # Unused
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
    ["", 0],
]

reg_fields = [
    # Regulatory Reporting Section
    ["Code", 8],  # = ''
    ["Country", 2],  # = ''
    ["Instruction 1", 33],  # = ''
    ["Instruction 2", 33],  # = ''
    ["Instruction 3", 33],  # = ''
]

b2b_fields = [
    # Bank-to-Bank Section
    ["Instruction Code 1", 4],  # = ''
    ["Instruction Text 1", 30],  # = ''
    ["Instruction Code 2", 4],  # = ''
    ["Instruction Text 2", 30],  # = ''
    ["Instruction Code 3", 4],  # = ''
    ["Instruction Text 3", 30],  # = ''
    ["Sender to Receiver Code 1", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Sender to Receiver Code 2", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Sender to Receiver Code 3", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Sender to Receiver Code 4", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Sender to Receiver Code 5", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Sender to Receiver Code 6", 8],  # = ''
    ["Sender to Receiver Text 1", 30],  # = ''
    ["Priority", 1],  # = 'No'
    ["", 0],
    ["Charges", 3],  # = 'Remitter'
    ["", 0],
    ["Additional Details", 35],  # = ''
]

other_fields = [
    # Note Section
    ["Note", 70],
    # Beneficiary Email Section
    ["Beneficiary Email", 60],
    # Transaction Information
    ["Payroll Indicator", 1],
    ["Confidential Indicator", 1],
    ["Group Name", 35],
    ["", 0],
    # Beneficiary Email Notification Section
    ["Email Address 1", 70],
    ["Email Address 2", 70],
    ["Email Address 3", 70],
]

fields = [
    record_fields,
    trx_fields,
    vd_fields,
    beneficiary_fields,
    ben_bank_fields,
    unused_1,
    int_bank_fields,
    obo_fields,
    unused_2,
    trx_det_fields,
    unused_3,
    reg_fields,
    b2b_fields,
    other_fields,
]

################
# Input Types
#   Record Information
#       1. Input Type - 2 - Free-form Trx = 'P'
#   Transaction Information
#       2. Method - 7 - WIRES or BOOKTX
#       3. Debit Bank ID - 11 - SWIFT BIC or ABA Identifier for originating account ordering the trx
#       4. Account Number - 34 - Account to be debited for the transaction (optionally zero-padded)
#       5. Bank-to-Bank Transfer - 1 - Used to indicate tfr between fin. institutions - default = 'N'
#       6. Currency - 3 - Currency of trx amount - valid ISO 4217 currency code
#       7. Payment Amount - 20,3 - The amount to be paid to beneficiary - use period to indicate decimal
#       8. Equivalent Amount - 20,3 - Amount denominated in the currency of the originating account (only for FX trx)
#       9. Clearing - 1 - leave blank
#       10. Beneficiary Residence - 1 - leave blank
#       11. Rate Type - 1 - Unused for same currency transactions
#       12. N/A - Leave Blank
#   Value Date Section
#       13. Value Date - 8 - Transaction value date in YYYYMMDD format. If left blank, defaults to 1st available day
#   Beneficiary Section
#       14. ID Type - 34 - Code to identify type of value supplied in the next field - see appendix B in JPM manual
#       15. ID Value - 34 - Beneficiary ID number, usually account number
#       16. Name - 35 - Name of beneficiary
#       17. Address 1 - 35 - street address
#       18. Address 2 - 35 - street address line 2
#       19. Address 3 - 32 - city, state, postal code
#       20. City, State, Postal Code - N/A - unused for wires and book tfrs
#       21. Country - 2 - ISO 3166 Country Code
#       22. Supplementary ID Type - 34 - Code to identify type of value supplied in supp. bank identifier field
#   Beneficiary Bank Section
#       23. Supplementary ID Value - 34 - Supplementary beneficiary bank identifier
#       24. ID Type - 34 - Code to identify value supplied in beneficiary bank identifier field (next field)
#       25. ID Value - 34 - Beneficiary bank identifier, usually SWIFT BIC or local clearing code
#       26. Name - 35 - Name of the beneficiary bank
#       27. Address 1 - 35 - Beneficary bank street address
#       28. Adrress 2 - 35 - Beneficiary bank street address 2
#       29. Address 3 - 32 - Beneficiary bank city, state, zip
#       30. Country - 2 - ISO 3166 Country Code
#       31. Supplementary ID Type - 34 - Code to identify value supplied in supp. bank identifer field (swift, BIC, ABA)
#       32. Supplementary ID Value - 34 - A supplementary bank beneficiary, can't be the same as the ID value earlier
#   Unused - 7 fields - must be present
#       33.
#       34.
#       35.
#       36.
#       37.
#       38.
#       39.
#   Intermediary Bank Section
#       40. ID Type - 34 - Type of ID supplied in next field (local clearing code, BIC, ABA)
#       41. ID Value - 34 - Intermediary bank identifier, which is usually SWIFT, BIC, or local clearing code
#       42. Name - 35 - Name of beneficiary bank
#       43. Address 1 - 35 - Beneficary bank street address
#       44. Adrress 2 - 35 - Beneficiary bank street address 2
#       45. Address 3 - 32 - Beneficiary bank city, state, zip
#       46. Country - 2 - ISO 3166 Country Code
#       47. Supplementary ID Type - 34 - Code to identify value supplied in supp. bank identifer field (swift, BIC, ABA)
#       48. Supplementary ID Value - 34 - A supplementary bank beneficiary, can't be the same as the ID value earlier
#   By Order Of Section - only populate if you are a financial instituion paying on behalf of a third party
#       49. ID Type
#       50. ID Value
#       51. Name
#       52. Address 1
#       53. Address 2
#       54. Address 3
#       55. Country
#   Unused - 18 fields - must be present and left blank
#       56.
#       ...
#       73.
#   Transaction Details Section
#       74. Reference Sent with Payment - 16 - free format reference text sent with trx
#       75. Internal Reference - 16 - free format reference text that does not show with transaction but will show on ordering side
#       76. On Behalf Of - 30 - when populated, field 80 (detail 4) must be unused
#       77. Detail 1 - 35 - Add'l info about transaction
#       78. Detail 2 - 35 - Add'l info about transaction
#       79. Detail 3 - 35 - Add'l info about transaction
#       80. Detail 4 - 35 - Add'l info about transaction
#   Unused - 8 fields - must be present and left blank
#       81.
#       ...
#       88.
#   Regulatory Reporting Section
#       89. Code - 8 - Regulatory reporting code - see JPM manual appendix A
#       90. Country - 2 - ISO 3166 country code
#       91. Instruction 1 - 21/33 - Regulatory deporting description - len = 21 if code and country are supplied
#       92. Instruction 2 - 33 - Regulatory reporting description
#       93. Instruction 3 - 33 - Regulatory reporting description
#   Bank-to-Bank Section
#       94. Instruction Code 1 - 4 - Include code as advised by JPM or beneficiary - see appendix A: instruction codes
#       95. Instruction Text 1 - 30 - free-format text - may be present if instruction code 1 supports add'l text
#       96. Instruction Code 2 - 4 - see appendix A: instruction codes - not applicable for US branch same-currency wires
#       97. Instruction Text 2 - 30 - free-format text - may be present if instruction code 2 supports add'l text
#       98. Instruction Code 3 - 4 - see appendix A: instruction codes - not applicable for US branch same-currency wires
#       99. Instruction Text 3 - 30 - free-format text - may be present if instruction code 3 supports add'l text
#       100. Sender to Receiver Code 1 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       101. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 1
#       102. Sender to Receiver Code 2 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       103. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 2
#       104. Sender to Receiver Code 3 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       105. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 3
#       106. Sender to Receiver Code 4 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       107. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 4
#       108. Sender to Receiver Code 5 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       109. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 5
#       110. Sender to Receiver Code 6 - 8 - Include code as advised by JPM or beneficiary - see appendix A: sender to receiver codes
#       111. Sender to Receiver Line 2 - 23-30 - Include instruction text as advised by JPM or beneficary - length varies dep on StR code 6
#       112. Priority - 1 - To indicate priority, must be 'Y', else 'N'
#       113. N/A - Leave blank
#       114. Charges - 3 - SHA = Shared / BEN = Beneficiary / OUR = Remitter - SHA not available for US accounts
#       115. N/A - Leave blank
#       116. Additional Details - Key|value pairs provide this info - See appendix A: add'l detail - key codes - destination currency and country primarily drive this
#   Note Section
#       117. Note - 70 - Free-format note for customer use, not transmitted
#   Beneficiary Email
#       118. Beneficiary Email - 60 - Beneficiary email, not transmitted with transaction
#   Transaction Information
#       119. Payroll Indicator - 1 - Used to indicate the transaction is payroll - Default is 'N'
#       120. Confidential Indicator - 1 - Used to indicate transaction is confidential - Default is 'N'
#       121. Group Name - 35 - Name tag which visually packages transactions together aiding workflow - can be leveraged by search
#       122. N/A - Leave blank
#   Email Payment Notification Information
#       123. Email Address 1 - 70 - Email address of beneficiary or other parties to notify - only available for some clients
#       124. Email Address 2 - 70 - Email address of beneficiary or other parties to notify - only available for some clients
#       125. Email Address 3 - 70 - Email address of beneficiary or other parties to notify - only available for some clients
