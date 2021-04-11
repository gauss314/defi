"""Summary
"""
import matplotlib.pyplot as plt
import pandas as pd
import datetime 
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def iloss(price_ratio):
    return 2 * (price_ratio**0.5 / (1 + price_ratio)) - 1





def compare(dias, var_A=0, var_B=0, rw_pool_A=0, rw_pool_B=0, rw_pool_AB=0, fees_AB=0):
    """Compare for 2 assets, buy&hold strategy with separate staking and farming by liquidity pool providing.
        Considering: impermanent loss, fees earned and farming/staking rewards
    
    Args:
        dias (int): days for strategy
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

    stake = buy_hold + 0.5 * dias * (rw_pool_A/100 + rw_pool_B/100)
    farm = buy_hold * (1+perdida_impermanente) + dias * (rw_pool_AB/100 + fees_AB/100)
    mejor = 'Farm' if farm > stake else 'Stake'
    
    return {'buy_hold':f'{buy_hold:.2%}', 'stake':f'{stake:.2%}', 'farm':f'{farm:.2%}', 'Best': mejor}