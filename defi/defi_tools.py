"""Tools for use in DeFi
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime, requests
from scipy import interpolate
import matplotlib.cm as cm


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





######################################################################
##                                                                  ##
##      Llama API                                                   ##
##      Public API https://docs.llama.fi/api                        ##
##                                                                  ##
######################################################################


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



######################################################################
##                                                                  ##
##      CoinGecko API                                               ##
##      Public API https://www.coingecko.com/es/api                 ##
##                                                                  ##
######################################################################




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



######################################################################
##                                                                  ##
##       Pancake Swap API                                           ##
##       API https://github.com/pancakeswap/pancake-info-api        ##
##                                                                  ##
######################################################################


def toFloatPartial(df):
    for i in df.columns:
        try:
            df[[i]] = df[[i]].astype(float)
        except:
            pass
    return df

        
def pcsSummary(as_df = True ):

    url = "https://api.pancakeswap.info/api/summary"
    r = requests.get(url).json()
    if as_df:
        return pd.DataFrame.from_dict(r, orient='index')
    else:
        return r

def pcsTokens(as_df = True):
    """get all token listed in pancakeswap
    
    Args:
        as_df (bool, optional): if True (default), return is a dataframe, else is a dictionary
    
    Returns:
        DataFrame with next columns: name  symbol  price   price_BNB   updated

    """
    # ultimo precio y volumen de base/quote de todos los pares

    url = "https://api.pancakeswap.info/api/tokens"
    r = requests.get(url).json()
    data = r.get('data', None)
    upd = r.get('updated_at')/1000
    upd_dt = datetime.datetime.fromtimestamp(upd)
    
    if as_df:
        df = pd.DataFrame.from_dict(data, orient='index')
        df = toFloatPartial(df) 
        df['updated'] = upd_dt
        return df
    else:
        return r


def pcsPairs(as_df = True):
    """get top 1000 pancakeswap pairs LP order by reserves
    
    Args:
        as_df (bool, optional): if True (default), return is a dataframe, else is a dictionary
    
    Returns:
        DataFrame with next columns: 'pair_address', 'base_name', 'base_symbol', 'base_address',
       'quote_name', 'quote_symbol', 'quote_address', 'price', 'base_volume',
       'quote_volume', 'liquidity', 'liquidity_BNB', 'updated'
    """

    url = "https://api.pancakeswap.info/api/pairs"
    r = requests.get(url).json()
    data = r.get('data', None)
    upd = r.get('updated_at')/1000
    upd_dt = datetime.datetime.fromtimestamp(upd)
    
    if as_df:
        df = pd.DataFrame.from_dict(data, orient='index')
        df = toFloatPartial(df) 
        df['updated'] = upd_dt
        return df
    else:
        return r

def pcsTokenInfo(search):
    """get info from a token
    
    Args:
        search (string): Token symbol or contract address
    
    Returns:
        Dict: 
        {
         'name': 'Wrapped BNB',
         'symbol': 'WBNB',
         'price': '524.5429',
         'price_BNB': '1'
         }
    """
    search = 'WBNB' if search.upper() == 'BNB' else search   
    url = "https://api.pancakeswap.info/api/tokens"
    r = requests.get(url).json()
    data = r.get('data', None)
    res = f"Not found: {search}"
    for contract, values in data.items():
        if search.upper() == values['symbol'].upper() or search.upper()==contract.upper():
            res = data[contract]
            break

    return res



def pcsPairInfo(base, quote):
    """get info from a token pair LP
    
    Args:
        base (string): Base LP token, ie "CAKE"
        quote (string): Quote LP token, ie "BNB"
        its the same if you call pcsPAirInfo('cake', 'bnb') or pcsPAirInfo('bnb', 'cake') 
    Returns:
        Dict: {
                 'pair_address': '0xA527a61703D82139F8a06Bc30097cC9CAA2df5A6',
                 'base_name': 'PancakeSwap Token',
                 'base_symbol': 'Cake',
                 'base_address': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
                 'quote_name': 'Wrapped BNB',
                 'quote_symbol': 'WBNB',
                 'quote_address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                 'price': '0.04311198194009326668',
                 'base_volume': '22248744.85',
                 'quote_volume': '934856.36',
                 'liquidity': '982769040.63',
                 'liquidity_BNB': '1878155.84'
                }
                * price is actually a ratio between base/quote tokens
    """
    url = "https://api.pancakeswap.info/api/pairs"
    r = requests.get(url).json()
    data = r.get('data', None)
    res = f"Not found: {base}-{quote}"
    base = 'WBNB' if base.upper() == 'BNB' else base
    quote = 'WBNB' if quote.upper() == 'BNB' else quote
    
    for contract, values in data.items():
        base_ = base.upper() == values['base_symbol'].upper()
        quote_ = quote.upper() == values['quote_symbol'].upper()
        base_cross = base.upper() == values['quote_symbol'].upper()
        quote_cross = quote.upper() == values['base_symbol'].upper()

        if  (base_ and quote_) or  (base_cross and quote_cross):
            res = data[contract]
            break
            
    return res


from scipy import interpolate
import matplotlib.cm as cm

def iloss_simulate(base_token, quote_token, value=100, base_pct_chg=0, quote_pct_chg=0):
    """Calculate simulated impermanent loss from an initial value invested, get real time prices from pancakeswap API
        This method create a 3D interpolated surface for impermanent loss and initial/final value invested

    Args:
        base_token (string): Pair first token, ie CAKE
        quote_token (string): Pais second token, ie BNB
        value (int, optional): Value investen in LP default=100
        base_pct_chg (int, optional): value assming will change first token of LP pair, ie 10 (for +10% change)
        quote_pct_chg (int, optional): value assming will change first token of LP pair, ie -30 (for -30% change)
    
    Returns:
        tuple (value_f, iloss): final value of value invested, and decimal impermanent loss
    """
    base_token = 'WBNB' if base_token.upper() == 'BNB' else base_token
    quote_token = 'WBNB' if quote_token.upper() == 'BNB' else quote_token
    
    # get real time prices
    tokens = pcsTokens()
    px_base = float(tokens.loc[tokens.symbol.str.upper()==base_token.upper()].price)
    px_quote = float(tokens.loc[tokens.symbol.str.upper()==quote_token.upper()].price)

    # Prepare grid
    q_base, q_quote = (value/2)/px_base,  (value/2)/px_quote
    px_base, px_quote, q_base, q_quote
    pxs_base = [px_base*i/100 for i in range(1,301)]
    pxs_quote = [px_quote*i/100 for i in range(1,301)]
    rows = []
    for px_b in pxs_base:
        for px_q in pxs_quote:
            ratio = (px_b / px_base) / (px_q / px_quote)
            iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1

            row = {'px_base':px_b, 'px_quote':px_q, 
                   'ratio':(px_b / px_base) / (px_q / px_quote),
                   'impremante_loss':iloss}
            rows.append(row)
    df = pd.DataFrame(rows)
    df_ok = df.loc[:,['px_base','px_quote','impremante_loss']]
    df_ok = df_ok.replace('NaN',np.nan).dropna()

    if all(isinstance(i, (int, float)) for i in (value, base_pct_chg, quote_pct_chg)):
        px_base_f = px_base * (1+base_pct_chg/100)
        px_quote_f = px_quote * (1+quote_pct_chg/100)
        ratio = (px_base_f / px_base) / ( px_quote_f / px_quote)
        iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
        value_f = (px_base_f*q_base + px_quote_f * q_quote) * (iloss+1)
    else:
        px_base_f, px_quote_f = px_base, px_quote
        iloss = 0
        value_f = None
        print('must input numerical amount and pct change for base and quote to calculations of final value')
        

    # Ploting surface
    fig = plt.figure(figsize=(8,8))
    x1 = np.linspace(df_ok['px_base'].min(), df_ok['px_base'].max(), len(df_ok['px_base'].unique()))
    y1 = np.linspace(df_ok['px_quote'].min(), df_ok['px_quote'].max(), len(df_ok['px_quote'].unique()))
    x2, y2 = np.meshgrid(x1, y1)
    Z = interpolate.griddata((df_ok['px_base'], df_ok['px_quote']), df_ok['impremante_loss'], (x2, y2))
    Z[np.isnan(Z)] = df_ok.impremante_loss.mean()
    ax = plt.axes(projection='3d', alpha=0.2)
    ax.plot_wireframe(x2, y2, Z, color='tab:blue', lw=1, cmap='viridis', alpha=0.6) 
        
    # Start values ploting
    xmax = df_ok.px_base.max() 
    ymax = df_ok.px_quote.max()
    ax.plot([px_base, px_base], [0,px_quote], [-1,-1], ls='--', c='k', lw=1)
    ax.plot([px_base, px_base], [px_quote,px_quote], [0,-1], ls='--', c='k', lw=1)
    ax.plot([px_base, 0], [px_quote, px_quote], [-1,-1], ls='--', c='k', lw=1)

    # End values ploting
    ax.plot([px_base_f, px_base_f], [0,px_quote_f], [-1,-1], ls='--', c='gray', lw=1)
    ax.plot([px_base_f, px_base_f], [px_quote_f,px_quote_f], [iloss,-1], ls='--', c='gray', lw=1)
    ax.plot([px_base_f, 0], [px_quote_f, px_quote_f], [-1,-1], ls='--', c='gray', lw=1)
    ax.plot([px_base_f, px_base_f], [px_quote_f,ymax], [iloss,iloss], ls='--', c='gray', lw=1)
    ax.plot([px_base_f, 0], [ymax,ymax], [iloss,iloss], ls='--', c='gray', lw=1)
    
    # Plot settings
    # Colorbar only for plot_surface() method instead plot_wireframe()
    # m = cm.ScalarMappable(cmap=cm.viridis) 
    # m.set_array(df_ok['impremante_loss'])
    # plt.colorbar(m, fraction=0.02, pad=0.1)
    x, y, z = (px_base, px_quote,.05)
    p = ax.scatter(x, y, z, c='k', marker='v', s=300)
    ax.set_title('Impermanent Loss 3D Surface', y=0.95)
    ax.set_xlabel(f'Price {base_token}')
    ax.set_ylabel(f'Price {quote_token}')
    ax.set_zlabel('Impremante loss')
    ax.view_init(elev=25, azim=240) # start view angle
    
    print (f"\nStart value USD {value:.0f}, {base} USD {px_base:.2f}, {quote} USD {px_quote:.2f}")    
    print(f"\nResults assuming {base.upper()} {base_pct_chg}%, and {quote.upper()} {quote_pct_chg}%")
    print (f"End value estimate USD {value_f:.0f}, iloss: {iloss:.2%}")
    plt.show()

    return value_f , iloss