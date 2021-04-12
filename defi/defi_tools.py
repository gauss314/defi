"""Tools for use in DeFi
"""
import matplotlib.pyplot as plt
import pandas as pd
import datetime, requests
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def iloss(price_ratio, numerical=False):
    """return the impermanent loss result in compare with buy&hold A&B assets

    
    Args:
        price_ratio (float): Variation A Asset / Variation B Asset
            
            price_ratio formula:
                price_ratio = (var_A/100 + 1) / (var_B/100 + 1)
                    var_A: Asset A % variation
                    var_B: Asset B % variation

        numerical (bool): if True, returns impermanent loss as a decimal expr, ie "5%"" => 0.05 (Default: False) 
    
    Returns:
        TYPE: impermanent loss as a string percentual value
    """
    il = 2 * (price_ratio**0.5 / (1 + price_ratio)) - 1
    r = f"{il:.2%}" if not numerical else il

    return r



def compare(days, var_A=0, var_B=0, rw_pool_A=0, rw_pool_B=0, rw_pool_AB=0, fees_AB=0):
    """Compare for 2 assets, buy&hold strategy with separate staking and farming by liquidity pool providing.
        Considering: impermanent loss, fees earned and farming/staking rewards
    
    Args:
        days (int): days for strategy
        var_A (float, optional): Percentual variation for A token. Ex 10 for 10%
        var_B (float, optional): Percentual variation for B token. Ex 10 for 10%
        rw_pool_A (float, optional): Percentual rewards per day for one asset pool (Token A)
        rw_pool_B (float, optional): Percentual rewards per day for one asset pool (Token B)
        rw_pool_AB (float, optional): Percentual rewards per day for two asset farm (LP Token AB)
        fees_AB (float, optional): Percentual provider liquidity fees earned per day
    
    Returns:
        dict: Percentual returns for each strategy:
            buy_hold two assets in your wallet
            stake two assets at individual pools
            farming by liquidity pool 
    """
    buy_hold = (0.5 * var_A + 0.5 * var_B)/100
    x = (var_A/100 + 1) / (var_B/100 + 1)
    perdida_impermanente = 2 * (x**0.5 / (1 + x)) - 1

    stake = buy_hold + 0.5 * days * (rw_pool_A/100 + rw_pool_B/100)
    farm = buy_hold * (1+perdida_impermanente) + days * (rw_pool_AB/100 + fees_AB/100)
    mejor = 'Farm' if farm > stake else 'Stake'
    
    return {'buy_hold':f'{buy_hold:.2%}', 'stake':f'{stake:.2%}', 'farm':f'{farm:.2%}', 'Best': mejor}


"""
Llama API

    Public API https://docs.llama.fi/api

"""

def getProtocols():
    """Get list all DeFi protocols across all blockchains
    
    Returns:
        DataFrame: All DeFi dApps 
    """
    url = "https://api.llama.fi/protocols"
    r = requests.get(url)
    r_json = r.json()
    df = pd.DataFrame(r_json)
    df.set_index('name', inplace=True)
    return df


def getProtocol(protocol):
    """Get metrics and historic TVL for one DeFi dApp
    
    Args:
        protocol (String): Name of protocol ie "Uniswap"
    
    Returns:
        tuple (Dictionary, DataFrame): Dictionary with protocol metadata & DataFrame with historical TVL
    """
    url = f"https://api.llama.fi/protocol/{protocol}"
    r = requests.get(url)
    r_json = r.json()

    df = pd.DataFrame(r_json['tvl'])
    df.date = pd.to_datetime(df.date, unit='s')
    df = df.set_index('date')
    del r_json['tvl']
    metadata = r_json

    return metadata, df


def getChart():
    """Get historical TVL across all DeFi dApps, cummulative result
    
    Returns:
        DataFrame: DataFrame date-indexed with all days TVL 
    """

    url  = "https://api.llama.fi/charts"
    r = requests.get(url)
    r_json = r.json()
    df = pd.DataFrame(r_json)
    df.date = pd.to_datetime(df.date, unit='s')
    df = df.set_index('date')
    return df



"""
coinGecko API

    Public API https://www.coingecko.com/es/api#explore-api

"""


def geckoPrice(tokens, quote):
    """get price of combine pairs
    
    Args:
        tokens (comma separated strings): ie "bitcoin,ethereum"
        quote (comma separated fiat or quote currency): ie: "usd,eur"
    
    Returns:
        dictionary: Returns pairs quotes
    """

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids":tokens, "vs_currencies":quote}
    r = requests.get(url, params).json()
    return r



def geckoList(page=1, per_page=250):
    """Returns list of full detail conGecko currency list
    
    Args:
        page (int, optional): number of pages
        per_page (int, optional): number of records per page
    
    Returns:
        DataFrame: list of full detail conGecko currency list
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency":"usd", "order":"market_cap_desc", "per_page":per_page, "page":page}
    r = requests.get(url, params).json()
    df = pd.DataFrame(r)
    df.set_index('symbol', inplace=True)
    return df



def geckoMarkets(ticker):
    """Get top100 markets (pairs, quotes, exchanges, volume, spreads and more)
    
    Args:
        ticker (string): gecko ID, ie "bitcoin"
    
    Returns:
        DataFrame: Full detail markets available
    """
    url = f"https://api.coingecko.com/api/v3/coins/{ticker}/tickers"
    r = requests.get(url).json()['tickers']
    df = pd.DataFrame(r)
    df['exchange'] = df['market'].apply(pd.Series)['name']
    df['volume_usd'] = df['converted_volume'].apply(pd.Series)['usd']
    df['price_usd'] = df['converted_last'].apply(pd.Series)['usd']

    df.set_index('exchange', inplace=True)
    cols = ['base','target','last', 'volume','bid_ask_spread_percentage','timestamp',
                   'volume_usd','price_usd','trust_score']
    df = df.loc[:,cols]
    cols[4] = 'spread'
    df.columns = cols
    df.timestamp = pd.to_datetime(df.timestamp)
    
    return df.sort_values('volume_usd', ascending=False)



def geckoHistorical(ticker, vs_currency='usd'):
    """Historical prices from coinGecko
    
    Args:
        ticker (string): gecko ID, ie "bitcoin"
        vs_currency (str, optional): ie "usd" (default)
    
    Returns:
        DataFrame: Full history: date, price, market cap & volume
    """
    url = f"https://api.coingecko.com/api/v3/coins/{ticker}/market_chart"
    params = {"vs_currency":{vs_currency}, "days":"max"}
    r = requests.get(url, params).json()
    prices = pd.DataFrame(r['prices'])
    market_caps = pd.DataFrame(r['market_caps'])
    total_volumes = pd.DataFrame(r['total_volumes'])
    df = pd.concat([prices, market_caps[1], total_volumes[1]], axis=1)
    df[0] = pd.to_datetime(df[0], unit='ms')
    df.columns = ['date','price','market_caps','total_volumes']
    df.set_index('date', inplace=True)

    return df