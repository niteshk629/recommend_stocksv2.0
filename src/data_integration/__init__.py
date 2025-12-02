"""Data Integration Module - Handles data fetching from multiple sources"""
from .yahoo_finance import YahooFinanceClient
from .groww_client import GrowwClient
from .zerodha_client import ZerodhaClient

__all__ = ['YahooFinanceClient', 'GrowwClient', 'ZerodhaClient']
