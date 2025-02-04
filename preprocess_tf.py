
def preprocessing_fn(norm_params, model_clusters, data=None):

    import pandas as pd

    # Load data as pandas df
    if isinstance(data, str):
        data = pd.read_csv(data, encoding='cp1252', index_col=None)
    elif isinstance(data, dict):
        data = pd.DataFrame(data)
    norm_params = pd.read_csv(norm_params, encoding='cp1252', index_col=None)
    model_clusters = pd.read_csv(model_clusters, encoding='cp1252', index_col=None)

    # select variables
    data = data.loc[:,['price','yearOfRegistration','gearbox','powerPS','model','kilometer','fuelType','notRepairedDamage']]

    # set data types
    data.price = data.price.astype('int32')
    data.yearOfRegistration = data.yearOfRegistration.astype('int32')
    data.gearbox = data.gearbox.astype('object')
    data.powerPS = data.powerPS.astype('int32')
    data.model = data.model.astype('object')
    data.kilometer = data.kilometer.astype('int32')
    data.fuelType = data.fuelType.astype('object')
    data.notRepairedDamage = data.notRepairedDamage.astype('object')

    # Fill NAs vehicle, fuel and gearbox with 'NA'
    data.fuelType = data.fuelType.fillna('_NA')
    data.loc[data.fuelType == 'other', 'fuelType'] = '_NA'
    data.gearbox = data.gearbox.fillna('_NA')
    data.loc[data.gearbox == 'other', 'gearbox'] = '_NA'

    # fill notRepairedDamage NAs with 'no'
    data.notRepairedDamage = data.notRepairedDamage.fillna('no')
    data.loc[data.notRepairedDamage == 'other', 'notRepairedDamage'] = 'no'
    
    # Add clustering column model
    data = pd.merge(data, model_clusters, on=['model'], how='left')
    data = data.drop(columns='model')
    ## Add another cluster for the NAs
    data.loc[data.cluster_model.isna(), 'cluster_model'] = model_clusters.cluster_model.max() + 1
    data.cluster_model = data.cluster_model.astype('int')


    # Numerical features normalization
    for num_col in ['yearOfRegistration', 'powerPS', 'kilometer']:
        if num_col == 'yearOfRegistration':
            data[num_col] = 2017 - data[num_col]  # feature as car age, we assume we are in 2017.
        data[num_col] = ((data[num_col] - norm_params.loc[norm_params.feature == num_col, 'mean'].values) / \
                        norm_params.loc[norm_params.feature == num_col, 'std'].values).astype('float32')
        data[num_col] = data[num_col].astype('float32')
        
    return data