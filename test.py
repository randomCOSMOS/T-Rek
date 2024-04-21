from datetime import datetime

def test(date = datetime.now()):
    print(date.strftime('%d-%m-%Y'))

date = "21/04/24"

test()