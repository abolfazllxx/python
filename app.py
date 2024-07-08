import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, PSARIndicator, ADXIndicator




class Strategy01():
    
    
    def __init__(
        self,
        short_ema_period : int,
        long_ema_period : int,
        psar_setup : tuple,
        adx_period : int
    ):
        
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period
        self.psar_setup = psar_setup
        self.adx_period = adx_period
        
        
    
    
    def create_indicator_values(
        self,
        price_data : pd.DataFrame
    ):
        
        # create df for saving indicators value
        indicator_df = pd.DataFrame( [] )
        
        # add datetime
        indicator_df[ "datetime" ] = price_data[ "datetime" ]
        
        
        # add 2 ema data
        short_ema = EMAIndicator(
            close = price_data[ "close" ],
            window = self.short_ema_period
        ) 
        
        indicator_df[ "short_ema" ] = short_ema.ema_indicator()
        
        long_ema = EMAIndicator(
            close = price_data[ "close" ],
            window = self.long_ema_period
        )
        
        indicator_df[ "long_ema" ] = long_ema.ema_indicator()
        
        
        # add psar data
        psar = PSARIndicator(
            high = price_data[ "high" ],
            low = price_data[ "low" ],
            close = price_data[ "close" ],
            step = self.psar_setup[0],
            max_step = self.psar_setup[1]
        )
        
        indicator_df[ "psar" ] = psar.psar()
        
        
        # add adx data
        adx = ADXIndicator(
            high = price_data[ "high" ],
            low = price_data[ "low" ],
            close = price_data[ "close" ],
            window = self.adx_period
        )
        
        indicator_df[ "adx" ] = adx.adx()
        indicator_df[ "adx_pos" ] = adx.adx_pos()
        indicator_df[ "adx_neg" ] = adx.adx_neg()
        
        
        return indicator_df
    
    
    # generate buy and sell signal
    
    def generate_buy_sell_signal(
        self,
        price_data : pd.DataFrame,
        indicator_data : pd.DataFrame
    ):
        
        
        signal_df = pd.DataFrame( [] )
        calculate_df = pd.DataFrame( [] )
        
        # add datetime
        signal_df[ "datetime" ] = price_data[ "datetime" ] 
        indicator_data[ "datetime" ] = price_data[ "datetime" ]
        
        # compare ema
        calculate_df[ "ema_compare" ] = np.where(
            indicator_data[ "short_ema" ] > indicator_data[ "long_ema" ],
            -1,
            np.where(
                indicator_data[ "short_ema" ] < indicator_data[ "long_ema" ],
                1,
                np.nan
            )
        )
        
        calculate_df[ "ema_compare" ] = np.where(
            (indicator_data[ "short_ema" ] == indicator_data[ "long_ema" ]) & ( indicator_data[ "short_ema" ] > 0),
            calculate_df[ "ema_compare" ].shift( periods = 1),
            calculate_df[ "ema_compare" ]
        )
        
        # compare psar 
        calculate_df[ "psar_compare" ] = np.where(
            indicator_data[ "psar" ] > price_data[ "close" ],
            -1,
            np.where(
                indicator_data[ "psar" ] < price_data[ "close" ],
                1,
                np.nan
            )
        )
        
        calculate_df[ "psar_compare" ] = np.where(
            ( indicator_data[ "psar" ] > price_data[ "close" ] ) & (price_data[ "close" ] > 0 ),
            calculate_df[ "psar_compare" ].shift( periods = 1),
            calculate_df[ "psar_compare" ]
        )
        
        # find allowed buy and allowed sell zone
        calculate_df[ "allowed_buy" ] = np.where(
            (calculate_df[ "ema_compare" ] == 1 ),
            1,
            0
        )
        
        calculate_df[ "allowed_sell" ] = np.where(
            (calculate_df[ "ema_compare" ] == -1 ) ,
            1,
            0
        )  
        
        calculate_df[ "generate_buy_signal" ] = np.where(
            ( calculate_df[ "psar_compare" ] == 1 ) & ( ( calculate_df[ "psar_compare" ].shift( periods = 1) == -1 )) & ( (indicator_data["adx"] >= 22.5) | (indicator_data["adx_neg"] >= 22.5)),
            1,
            0
        )    
        
        calculate_df[ "generate_sell_signal" ] = np.where(
            ( calculate_df[ "psar_compare" ] == -1 ) & ( ( calculate_df[ "psar_compare" ].shift( periods = 1) == 1 )) & ( (indicator_data["adx"] >= 22.5) | (indicator_data["adx_pos"] >= 22.5)),
            1,
            0            
        ) 
        
        signal_df[ "buy_signal" ] = np.where(
            ( calculate_df[ "generate_buy_signal" ] == 1 ) & ( calculate_df[ "allowed_buy" ] == 1 ),
            1,
            0
        )
        
        signal_df[ "sell_signal" ] = np.where(
            ( calculate_df[ "generate_sell_signal" ] == 1 ) & ( calculate_df[ "allowed_sell" ] == 1 ),
            1,
            0            
        )
        return signal_df
    
if __name__ == "__main__":
    
    data = pd.read_csv(
        filepath_or_buffer = "AUDNZD.csv"
    )
    
    strategy = Strategy01(
        short_ema_period = 50,
        long_ema_period = 100,
        psar_setup = ( 0.02, 0.2),
        adx_period = 12
    )
    
    indicators = strategy.create_indicator_values(
        price_data = data
    )
    
    signal = strategy.generate_buy_sell_signal(
        price_data = data,
        indicator_data = indicators
    )
    
    print( signal[ ( signal["buy_signal"] == 1) | ( signal["sell_signal"] == 1 ) ] )
