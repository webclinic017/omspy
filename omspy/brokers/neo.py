from omspy.base import Broker, post, pre
from typing import Optional, List, Dict, Union
from neo_api_client import NeoAPI
import pendulum
import logging


class Neo(Broker):
    """
    Automated trading class for Neo Broker
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        mobilenumber: str,
        password: str,
        twofa: str,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        self._user_id = user_id
        self._mobilenumber = mobilenumber
        self._password = password
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._mpin = twofa
        self._kwargs = kwargs
        super(Neo, self).__init__()
        client = NeoAPI(
            consumer_key=self._consumer_key,
            consumer_secret=self._consumer_secret,
            **self._kwargs,
        )
        self.neo = client

    def authenticate(self) -> Dict:
        self.neo.login(
            password=self._password,
            mobilenumber=self._mobilenumber,
        )
        return self.neo.session_2fa(self._mpin)

    @pre
    def order_place(self, **kwargs) -> Union[str, None]:
        """
        place an order
        """
        try:
            order_args = dict(
                exchange_segment="NSE",
                product="MIS",
                order_type="MKT",
                validity="DAY",
            )
            order_args["transaction_type"] = kwargs.pop("transaction_type").upper()[0]
            for key in ("quantity", "price", "trigger_price", "disclosed_quantity"):
                val = str(kwargs.pop(key, 0))
                order_args.update({key: val})
            order_args.update(kwargs)
            response = self.neo.place_order(**order_args)
            if response.get("Error"):
                logging.error(response["Error"])
                return None
            elif response.get("error"):
                logging.error(response["error"])
                return None
            else:
                return response.get("nOrdNo")
        except Exception as e:
            logging.error(e)
            return None

    @pre
    def order_modify(self, order_id: str, **kwargs) -> Optional[Dict]:
        """
        modify the order
        """
        modify_args = dict(validity="DAY", product="MIS", amo="NO")
        for key in ("quantity", "price", "trigger_price", "disclosed_quantity"):
            if key in kwargs:
                kwargs[key] = str(kwargs[key])
        modify_args.update(kwargs)
        response = self.neo.modify_order(order_id=order_id, **modify_args)
        return response

    def order_cancel(self, order_id: str):
        """
        cancel an existing order
        """
        response = self.neo.cancel_order(order_id=order_id)
        return response

    @property
    @post
    def orders(self) -> List[Dict]:
        """
        return the list of orders
        """
        response = self.neo.order_report()
        if "data" in response:
            orderbook = response["data"]

            for o in orderbook:
                o["ordSt"] = str(o["ordSt"]).upper()
            return orderbook
        else:
            logging.warning(response)
            return [{}]
