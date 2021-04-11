# Tools for use in DeFi

## Instalación


```sh
pip install defi
```


## Example

```python
import defi.defi_tools as dft

# Impermanent loss for stableCoin & -20% return token 
dft.iloss(0.8)
```
-0.62%



```python
import defi.defi_tools as dft

# Impermanent loss for stableCoin & +60% return token 
dft.iloss(1.6)
```
-2.7%




```python
import defi.defi_tools as dft

dft.compare(days=20, var_A=0, var_B=150, rw_pool_A=0.01, rw_pool_B=0.05, rw_pool_AB=0.2, fees_AB=0.01)
```
{
 'buy_hold': '75.00%',
 'stake': '75.60%',
 'farm': '71.96%',
 'Mejor Estrategia': 'Stake'
}


## About

Utilizamos las librerías:
- twitter user @JohnGalt_is_www