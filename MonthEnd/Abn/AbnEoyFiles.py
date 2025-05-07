from FileGrabber import AbnFileGrabber

##### PROCESS NOTES #####
# MARK TO MARKET OPTIONS LONG/SHORT ARE NETTED TO MARK TO MARKET OPTIONS
# MARK TO MARKET UNSETTLED LONG/SHORT STOCK ARE NETTED TO MARK TO MARKET UNSETTLED STOCK
# MARK TO MARKET UNSETTLED LONG/SHORT PREFSTOCK ARE NETTED TO MARK TO MARKET UNSETTLED PREFSTOCK
#   ADD PRIOR VALUES FOR THESE TO THE RESULTING FILE AND ZERO OUT THE NETTED CATEGORIES
#
# GROSS PROFIT OR LOSS IS A FUTURES ONLY CATEGORY AND IS NETTED INTO BALANCE PREVIOUS YEAR
#   THIS CAN STAY UNTOUCHED
#
# OPEN TRADE EQUITY IS LISTED AS OPEN TRADE EQUITY FUTURES BUT STAYS THE SAME
#   THIS NEEDS TO BE RENAMED FOR VALUES TO COME THROUGH


def test_2024():
    grabber = AbnFileGrabber(2024, 12)
    summary_df = grabber.AbnEoyFile(2024)

    try:
        summary_df.to_csv('C:/gdrive/Shared drives/accounting/Simplex Trading/2025/ABN/EOY Cash File.csv', index=False)
    except PermissionError:
        print('Close file before continuing')
        input()
    finally:
        summary_df.to_csv('C:/gdrive/Shared drives/accounting/Simplex Trading/2025/ABN/EOY Cash File.csv', index=False)