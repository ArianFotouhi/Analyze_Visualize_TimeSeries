Date_col ='DATE_UTC'
CLName_Col = 'CLIENT_NAME'
Lounge_ID_Col = 'lounge_name'
Volume_ID_Col = 'COUNT_PAX_ALLOWED'
Refuse_Col='COUNT_PAX_REFUSED'
Ratio_Col='REF2ALW'

time_alert = 20

users = {
    "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['LH','LX','MAG']},

    "user1": {"password": "pass", "ClientID": 1 , 'AccessCL':['MAG','LX']},
    "user2": {"password": "pass", "ClientID": 2, 'AccessCL':['LH']},
    "user3": {"password": "pass", "ClientID": 3, 'AccessCL':['LX']},
}
