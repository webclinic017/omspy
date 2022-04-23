from omspy.base import Broker, pre, post
from typing import Optional, List, Dict, Union
from ks_api_client import ks_api
import pendulum
import pandas as pd
import logging


def get_url(segment: Optional[str] = "cash") -> str:
    dt = pendulum.now(tz="Asia/Kolkata")
    date_string = dt.strftime("%d_%m_%Y")
    dct = {"cash": "Cash", "fno": "FNO"}
    seg = dct.get(segment, "Cash")
    url = f"https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_{seg}_{date_string}.txt"
    return url


def get_name_for_cash_symbol(
    instrument_name: str, instrument_type: Optional[str] = None
):
    """
    Get the broker interface name for a symbol in cash segment
    """
    if instrument_type is None:
        pass
    elif pd.isna(instrument_type):
        instrument_type = None
    elif not (instrument_type.isalnum()):
        instrument_type = None
    elif instrument_type.upper() == "EQ":
        instrument_type = None
    elif instrument_type.lower() in ("na", "nan"):
        instrument_type = None

    if instrument_type is None:
        return instrument_name
    else:
        return f"{instrument_name}-{instrument_type or False}"


def get_name_for_fno_symbol(
    instrument_name: str,
    expiry: Union[pendulum.Date, pendulum.DateTime, str],
    option_type: Optional[str] = None,
    strike: Optional[Union[float, int]] = None,
):
    """
    Get the broker interface name for a future or option symbol
    Note
    -----
    1)If either the option type or option strike argument is not given, it is considered a futures contract
    2) A contract is considered an option contract only if both option type and strike price is provided
    """
    if isinstance(expiry, str):
        expiry = pendulum.parse(expiry)
    expiry = expiry.strftime("%d%b%y").upper()

    # Set the option type
    opts = {"ce": "call", "pe": "put"}
    if option_type is None:
        option_type = None
    elif pd.isna(option_type):
        option_type = None
    elif not (isinstance(option_type, str)):
        option_type = None
    elif option_type.lower() not in ("ce", "pe"):
        option_type = None
    else:
        option_type = opts.get(option_type.lower())

    # Set the strike
    if strike is None:
        strike = None
    elif not (isinstance(strike, (int, float))):
        strike = None
    elif strike <= 0:
        strike = None

    # Consider an instrument futures if there is no
    # corresponding strike or option type
    if (option_type is None) or (strike is None):
        return f"{instrument_name}{expiry}FUT".upper()
    else:
        return f"{instrument_name}{expiry}{strike}{option_type}".upper()


def download_file(url: str) -> pd.DataFrame:
    """
    Given a url, download the file, parse contents
    and return a dataframe.
    returns an empty Dataframe in case of an error
    """
    try:
        df = pd.read_csv(url, delimiter='|', parse_dates=['expiry'])
        df = df.rename(columns = lambda x:x.lower())
        return df.drop_duplicates(subset=['instrumenttoken'])
    except Exception as e:
        logging.error(e)
        return pd.DataFrame()

def add_name(data, segment:Optional[str]="cash")->pd.DataFrame:
    """
    add name to the given dataframe and return it
    data
        dataframe with the instrument data
    segment
        segment to add name to either cash or fno
    Note
    -----
    1) The extra column added is inst_name
    """
    if segment.lower() == "cash":
        data['inst_name'] = [f"{k}:{get_name_for_cash_symbol(x,y)}" for x,y,k in zip (data.instrumentname.values, data.instrumenttype.values,data.exchange.values)]
        return data
    elif segment.lower() == "fno":
        data['inst_name'] = [f"{k}:{get_name_for_fno_symbol(a,b,c,d)}" for a,b,c,d,k in zip(data.instrumentname.values, data.expiry.values, data.optiontype.values,data.strike.values,data.exchange.values)]
        return data
    else:
        return data


class Kotak(Broker):
    """
    Automated Trading class
    """

    def __init__(
        self,
        access_token: str,
        userid: str,
        password: str,
        consumer_key: str,
        access_code: Optional[str] = None,
        ip: str = "127.0.0.1",
        app_id: str = "default",
    ):
        pass

    def get_instrument_token(self, **kwargs) -> int:
        pass

    def authenticate(self) -> None:
        pass

    def orders(self) -> List[Dict]:
        pass

    def positions(self) -> List[Dict]:
        pass

    def trades(self) -> List[Dict]:
        pass

    def order_place(self, **kwargs) -> Dict:
        pass

    def order_cancel(self, **kwargs) -> Dict:
        pass

    def order_modify(self, **kwargs) -> Dict:
        pass