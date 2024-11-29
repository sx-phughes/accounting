header_fields = [
    ['HEADER', 7], # = 'HEADER'
    ['File Timestamp', 14], # = 'YYYYMMDDHHMMSS'
    ['Version', 5] # 5 including decimal indicator
]

trailer_fields = [
    ['TRAILER', 7], # = 'TRAILER'
    ['Total Number of Records', 23],
    ['Hash Total Amount', 17] # sum of all trx in file
]

record_fields = [
    ['Input Type', 2] # PT
]

trx_info_fields = [
    ['Debit/Credit Bank ID', 11],
    ['Account Number', 34],
    ['Template Name', 40],
    ['Enhanced Template Line Number', 10], # blank
    ['Payment Amount', 24],
    ['Equivalent Amount', 24], # blank
    ['Rate Type', 1]
]

vd_fields = [
    ['Value Date', 8] # YYYYMMDD
]

trx_det_fields = [
    ['Reference Sent with Payment', 74], # free format text sent w pmt
    ['Internal Reference', 16], # not sent, optional
    ['Detail 1', 35], 
    ['Detail 2', 35],
    ['Detail 3', 35],
    ['Detail 4', 35],
    ['Detail 5', 35], # unused
    ['Detail 6', 35], # unused
    ['Detail 7', 35], # unused
    ['Detail 8', 35], # unused
    ['Detail 9', 35], # unused
    ['Detail 10', 35], # unused
    ['Detail 11', 35], # unused
    ['Detail 12', 35] # unused
]

reg_fields = [
    ['Code', 8], # unused
    ['Country', 2], # ISO 3166 country code
    ['Instruction 1', 21], # unused
    ['Instruction 2', 33], # unused
    ['Instruction 3', 33], # unused
]

b2b_fields = [ 
    ['Instruction Code 1', 4], 
    ['Instruction Text 1', 30],
    ['Instruction Code 2', 4],
    ['Instruction Text 2', 30],
    ['Instruction Code 3', 4],
    ['Instruction Text 3', 30],
    ['Sender to Receiver Code 1', 8],
    ['Sender to Receiver Line 1', 23],
    ['Sender to Receiver Code 2', 8],
    ['Sender to Receiver Line 2', 23],
    ['Sender to Receiver Code 3', 8],
    ['Sender to Receiver Line 3', 23],
    ['Sender to Receiver Code 4', 8],
    ['Sender to Receiver Line 4', 23],
    ['Sender to Receiver Code 5', 8],
    ['Sender to Receiver Line 5', 23],
    ['Sender to Receiver Code 6', 8],
    ['Sender to Receiver Line 6', 23],
    ['Priority', 1], # N
    ['Urgent', 1], # N
    ['Charges', 0],
    ['Additional Details',0]
]

note_field = [
    ['Note', 70]
]

ben_email_field = [
    ['Email Address 1', 70],
    ['Email Address 2', 70],
    ['Email Address 3', 70]
]



template_fields = [
    record_fields,
    trx_info_fields,
    vd_fields,
    trx_det_fields,
    reg_fields,
    b2b_fields,
    note_field,
    ben_email_field
]