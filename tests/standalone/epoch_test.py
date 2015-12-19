import datetime
from dateutil.parser import parse
import time


def convert_strdate_to_timestamp(value):
    # check sysdate type
    print("convert_sysdate input: " + str(value))
    print("convert_sysdate input_type: " + str(type(value)))

    timestamp = None
    # now in epoch time
    epoch_now = int(time.time())

    if isinstance(value, int):
        timestamp = value
    elif isinstance(value, datetime.date):
        timestamp = (value - datetime.datetime(1970, 1, 1)).total_seconds()
    elif value:

        value = str(value)

        if isinstance(value, str):
            try:
                the_date = parse(value)
                print("DEBUG parsed date: " + str(the_date))
                # woks for poython 3
                # timestamp = the_date.timestamp()
                timestamp = time.mktime(the_date.timetuple())

            except Exception as e:
                print(e.message)
                print('WARN model sysdate impossible to parse: ' + str(value))
                timestamp = epoch_now
    else:
        # Value is None
        timestamp = epoch_now

    return timestamp


def main():
    input = "2011-11-11 11:11:11"
    res = convert_strdate_to_timestamp(input)
    print('res: ' + str(res))
    print('convert in: ' + str(datetime.datetime.fromtimestamp(res)))

if __name__ == '__main__':
    main()
