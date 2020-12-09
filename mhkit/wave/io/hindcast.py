import pandas as pd
import numpy as np
from rex import WaveX, MultiYearWaveX

def request_wpto_dataset(data_type, parameter, lat_lon, years, tree=None, 
                                 unscale=True, str_decode=True,hsds=True):
    
        """
        Accesses data from the WPTO wave hindcast data hosted on AWS. 

        Note: To access the WPTO hindcast data, you will need to configure h5pyd for data access on HSDS. 
        To get your own API key, visit https://developer.nrel.gov/signup/. 

        To configure h5phd type 
        hsconfigure
        and enter at the prompt:
        hs_endpoint = https://developer.nrel.gov/api/hsds
        hs_username = None
        hs_password = None
        hs_api_key = {your key}
        Parameters
        ----------
        data_type : string
            data set type of interst
            Options: 'spatial'
        parameter: string
            dataset parameter to be downloaded
            spatial dataset options: 'directionality_coefficient', 'energy_period', 'maximum_energy_direction'
                'mean_absolute_period', 'mean_zero-crossing_period', 'omni-directional_wave_power', 'peak_period'
                'significant_wave_height', 'spectral_width', 'water_depth' 
        lat_lon: tuple or list of tuples
            latitude longitude pairs at which to extract data 
        years : list 
            List of years to access. The years 1979-2010 available. Examples: [1996] or [2004,2006,2007]
        tree : str | cKDTree (optional)
            cKDTree or path to .pkl file containing pre-computed tree
            of lat, lon coordinates, default = None
        unscale : bool (optional)
            Boolean flag to automatically unscale variables on extraction
            Default = True
        str_decode : bool (optional)
            Boolean flag to decode the bytestring meta data into normal
            strings. Setting this to False will speed up the meta data read.
            Default = True
        hsds : bool (optional)
             Boolean flag to use h5pyd to handle .h5 'files' hosted on AWS
             behind HSDS. Setting to False will indicate to look for files on 
             local machine, not AWS. Default = True

        Returns
        ---------
        data: DataFrame 
            Data indexed by datetime with columns named for parameter and lat_lon 
        meta: DataFrame 
            location metadata for the requested data location   
        """
        
        assert isinstance(parameter, (str, list)), 'parameter must be of type string or list'
        assert isinstance(lat_lon, (list,tuple)), 'lat_lon must be of type list or tuple'
        assert isinstance(data_type, str), 'data_type must be a string'
        assert isinstance(years,(list,int)), 'years must be a list'
        assert isinstance(tree,(str,type(None))), 'tree must be a sring'
        assert isinstance(unscale,bool), 'unscale must be bool type'
        assert isinstance(str_decode,bool), 'str_decode must be bool type'
        assert isinstance(hsds,bool), 'hsds must be bool type'

        if data_type == 'spatial':
            wave_path = f'/nrel/US_wave/US_wave_*.h5'
        else:
            print(f'ERROR: invalid data_type')
            pass
        
        data_list = []
        if isinstance(years,list):
            waveKwargs = {'tree':tree,'unscale':unscale,'str_decode':str_decode, 'hsds':hsds,
            'years':years}
            rex_accessor = MultiYearWaveX
        else:
            waveKwargs = {'tree':tree,'unscale':unscale,'str_decode':str_decode, 'hsds':hsds}
            rex_accessor = WaveX
            
        with rex_accessor(wave_path, **waveKwargs) as rex_waves:
            if isinstance(parameter, list):
                for p in parameter:
                    temp_data = rex_waves.get_lat_lon_df(p,lat_lon)
                    col = temp_data.columns[:]
                    if isinstance(lat_lon[0], (list,tuple)):
                        for c,l in zip(col,lat_lon):
                            temp = f'{p}_{l[0]}_{l[1]}'
                            temp_data = temp_data.rename(columns={c:temp})
                    else:
                        temp = f'{p}_{lat_lon[0]}_{lat_lon[1]}'
                        temp_data = temp_data.rename(columns={col[0]:temp})
                    data_list.append(temp_data)
                data= pd.concat(data_list)
                meta = rex_waves.meta.loc[col,:]
            else:
                data = rex_waves.get_lat_lon_df(parameter,lat_lon)
                col = data.columns[:]
                meta = rex_waves.meta.loc[col,:]
                if isinstance(lat_lon[0], (list,tuple)):
                    for c,l in zip(col,lat_lon):
                        temp = f'{parameter}_{l[0]}_{l[1]}'
                        data = data.rename(columns={c:temp})
                else:
                    temp = f'{parameter}_{lat_lon[0]}_{lat_lon[1]}'
                    data = data.rename(columns={col[0]:temp})
                
        return data, meta