# %% IMPORT STATEMENTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from lightgbm import LGBMRegressor
import os

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.model_selection import TimeSeriesSplit, cross_validate, GridSearchCV, ParameterGrid
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor, RegressorChain
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.svm import SVR

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import pacf, adfuller, arma_order_select_ic
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pmdarima.arima import auto_arima, ndiffs

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import warnings
warnings.filterwarnings('ignore')
import sys 
sys.path.append(r'c:\Users\ruben\OneDrive\Documents\dash')
import plot_df as pdf

pd.options.display.float_format = '{:.2f}'.format


# %% LOAD WALMART
# # Load specifically for Wlamart dataset

# # Load the data C:\Users\ruben
# df_raw_source = pd.read_csv(r'c:\users\ruben\train.csv')
# df_test = pd.read_csv(r'c:\users\ruben\test.csv')
# df_stores = pd.read_csv(r'c:\users\ruben\stores.csv')
# df_features = pd.read_csv(r'c:\users\ruben\features.csv')

# df_train = df_raw_source.copy()
# df_train = df_train.merge(df_features.drop(columns=['IsHoliday']), on=['Store', 'Date'], how='left')
# df_train.drop(columns = ['Store', 'Dept'], inplace = True)
# df_train = df_train.fillna(0)
# df_train.set_index('Date', inplace=True)

# %% LOAD BIKESHARE

bike_sharing = fetch_openml("Bike_Sharing_Demand", version=2, as_frame=True)
df_source_raw = bike_sharing.frame

df_source_raw["weather"] = (
   df_source_raw["weather"]
    .astype(object)
    .replace(to_replace="heavy_rain", value="rain")
    .astype("category")
)

df_source_raw = df_source_raw[(df_source_raw['hour'].isin([11,12,13,14,15,16,17,18,19,20,21,22,23])) & (df_source_raw['year'] == 1)]
df_source_raw = df_source_raw[df_source_raw['hour'].isin([12 , 13, 14 ,15 ,16 ])]

time_split = pd.to_datetime('2016-03-31')

df_source_raw = df_source_raw.sort_values(by=['hour', 'month'])
df_source_raw['date'] = pd.date_range(start='1/3/2013', periods = len(df_source_raw))


df_source_raw.set_index('date', inplace=True, drop=True)
df_source_raw.drop(columns=['season', 'year', 'hour', 'weekday'], inplace=True)

df_source_raw = df_source_raw[df_source_raw.index < pd.to_datetime('2018-01-01')]     # Cut off the data so that there are no partial months

df_source_raw['time_step'] = range(1, len(df_source_raw) + 1)

monthly_counts = df_source_raw.resample('M')['count'].sum()

# %%
class cyclical_transformer(BaseEstimator, TransformerMixin):
    def __init__(self, mdict):
        self.mdict = mdict
        self.get_features = []

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        if not isinstance(X, pd.DataFrame):X = pd.DataFrame(X)
        
        for i in self.mdict.keys():
            if i in X.columns:
                X[i + '_sin'] = np.sin(2 * np.pi * X[i] / self.mdict[i])
                X[i + '_cos'] = np.cos(2 * np.pi * X[i] / self.mdict[i])
                #X.drop(i, axis=1, inplace=True)
            else:
                print(f'Column {i} not found in dataframe')

        self.get_features = [i + '_sin' for i in self.mdict.keys()] + [i + '_cos' for i in self.mdict.keys()] #+ [i for i in self.mdict.keys()]
        X.drop(columns=list(self.mdict.keys()), inplace=True)
        return X 

    def get_feature_names_out(self, input_features=None):
        return self.get_features
class passthrough(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):X = pd.DataFrame(X)
        return X
    
    def get_feature_names_out(self, input_features):
        return input_features
class create_lags(BaseEstimator, TransformerMixin):
    def __init__(self, mdict):
        self.mdict = mdict
        self.get_features = []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        lag_list_holder = []                                        #
        #{'count': 12}
        for lag_i, lag_j in self.mdict.items():
            if isinstance(lag_j, list):                     # Lags for a given list
                for i in lag_j: 
                    X[f'lagged{i}'] = X[lag_i].shift(i)
                    lag_list_holder.append(f'lagged{i}')
            else:                                           # Lags for a given range
                for i in range(1, lag_j + 1):
                    X[f'lagged{i}'] = X[lag_i].shift(i)
                    lag_list_holder.append(f'lagged{i}')
        X.drop(columns=list(self.mdict.keys()), inplace=True)
        self.get_features = lag_list_holder
        return X 

    def get_feature_names_out(self, input_features=None):
        return self.get_features
class pipeline():
    def __init__(self, data, numeric_encode=[], categorical_encode=[], cyclical_col={}, lag_dict= {}, target='count'):
        
        self.data = data
        self.transformed_data = None
        self.target = None
        self.preprocessor = None

        self.numeric_encode = numeric_encode
        self.categorical_encode = categorical_encode
        
        self.cyclical_col = cyclical_col        # cyclical_col={'month': 12}
        self.lag_dict = lag_dict                # lag_dict={'count': [1,7]}
        self.lag_list = list(lag_dict.keys())

        features = list(self.data.columns)
        self.all_features = features
        features.remove(target)

        self.categorical_col = self.data.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
        self.numeric_col = self.data.select_dtypes(include=['int64', 'float64']).columns.tolist()

        fitted_preprocessor = self.fit_pipeline(features, target)

        df_X_train = pd.DataFrame(fitted_preprocessor.transform(self.data)
                                  , columns=fitted_preprocessor.get_feature_names_out())  
        
        df_X_train = df_X_train.set_index(self.data.index)
        self.transformed_data = df_X_train.dropna()

    def __repr__(self):
        represent = f"Pipeline object with data shape {self.data.shape} \n \
                    , target : {self.target} \n \
                    , cyclical columns {self.cyclical_col} \n \
                    , lag columns :{self.lag_dict} \n \
                    , numeric columns :{self.numeric_col} \n \
                    , numeric encoded columns :{self.numeric_encode} \n \
                    , categorical columns :{self.categorical_col} \n \
                    , categorical encoded columns :{self.categorical_encode}"
        return represent
   
    def fit_pipeline(self, features, target):
        # numeric_col, categorical_col, cyclical_col
        
        categorical_encode = [col for col in self.categorical_encode if col in features]
        numeric_encode = [col for col in self.numeric_encode if col not in self.lag_list
                                                 and col not in self.cyclical_col.keys() 
                                                 and col != target
                                                 and col in features]    
        
        pass_list = [col for col in features if
                         col not in numeric_encode 
                         and col not in categorical_encode
                         and col in self.all_features] #and col not in self.cyclical_col.keys()]
        pass_list = pass_list + [target]
        
        preprocessor = ColumnTransformer(
        transformers=[
            ('cyclical', cyclical_transformer(self.cyclical_col), list(self.cyclical_col.keys())),              # Cyclical transformation for month
            ('num', StandardScaler(), numeric_encode),                                                  # Standard scaling for numeric features
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_encode),      # One-hot encoding for categorical features
            ('lags', create_lags(self.lag_dict), self.lag_list),
            ('passthrough', passthrough(), pass_list)
            ]
        , remainder='drop'                                                                           # Pass through any remaining columns
        , verbose_feature_names_out=False
        )

        preprocessor.fit(self.data)
        self.preprocessor = preprocessor
        return preprocessor
       
    def get_relevant_columns(self, features, target):
        a_col = list(self.fit_pipeline(features, target).get_feature_names_out())
        if target in a_col: a_col.remove(target)
        return a_col
    
    def get_train_test_split(self, split_date = time_split ):
        df = self.transformed_data
        split = pd.to_datetime(split_date)
        next_day = split + pd.Timedelta(1, "d")

        df_source = df.loc[:split, :]
        df_source_test  = df.loc[next_day:, :]

        return df_source, df_source_test
    
class fitted_model:
  def __init__(self, target = None, predictors = None, model=None, error = None, score = None, model_key = None, params = None, cv = None):
    self.model_key = model_key
    self.error = error
    self.target = target
    self.predictors = predictors
    self.model = model
    self.score = score
    self.params = params
    self.cv = cv
# Check nulls and impute any missing variable
def check_nulls(data):
    missing_df = data.isnull().sum(axis=0).reset_index()
    missing_df.columns = ['variable', 'missing values']
    missing_df['filled (%)']=(data.shape[0]-missing_df['missing values'])/data.shape[0]*100

    # Check for duplicates rows
    has_duplicates = data.duplicated().any()
    print(f"\n Does the DataFrame have any duplicate rows? {has_duplicates}")
    missing_df['type'] = pd.Series(data.dtypes).values
    return missing_df
def is_stationary(series, significance_level=0.05):
    if isinstance(series, np.ndarray):
        series = pd.Series(series)

    result = adfuller(series)
    p_value = result[1]

    kpss_diffs = ndiffs(series , alpha=0.05, test='kpss', max_d=6)
    adf_diffs = ndiffs(series, alpha=0.05, test='adf', max_d=6)
    n_diffs = max(adf_diffs, kpss_diffs)

    pacf_values = pacf(series, nlags=30)

    confidence_interval = 2.58 / np.sqrt(len(series))
    significant_lags = np.where(np.abs(pacf_values) > confidence_interval)[0]   # Identify significant lags
    ord_lag = np.argsort(np.abs(pacf_values))[::-1][:len(significant_lags)]
    print('diff', n_diffs)

    return p_value < significance_level, n_diffs, significant_lags, ord_lag
def check_autocorrelation(series, lags=30):
  aa, bb, cc, dd = is_stationary(series)
  print(f"Is target stationary? ",aa)
  print(f"Number of differencing terms needed: ", bb)
  print(f"Significant lags: ",cc)
  print(f"Significant lags(ordered): ",dd)

  df_lags = pd.DataFrame()
  for i in range(1, lags + 1):
    df_lags[f'lag_{i}'] = series.shift(i)

  corr_matrix = df_lags.dropna().corr()

  # Plot PACF
  fig, axes = plt.subplots(1, 3, figsize=(18, 4))
  plot_acf(series, lags=30, ax=axes[0])
  plot_pacf(series, lags=30, ax=axes[1])
  sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0, ax=axes[2])
  plt.xlabel('Lag')
  plt.ylabel('Partial Autocorrelation')
  plt.title('Lag plot')
  plt.show()

# Returns best_model, performance_stats series, forecast
def fit_poisson_model(pipe_in, features, target, family):

    df_train, df_test = pipe_in.get_train_test_split(split_date= time_split)
    mod_features = pipe_in.get_relevant_columns(features, target)

    X_train = df_train[mod_features]
    y_train = df_train[target]
    X_test = df_test[mod_features]
    y_test = df_test[target]

    X_train = sm.add_constant(X_train)
    X_test = sm.add_constant(X_test)

    model_poisson_in = sm.GLM(y_train, X_train, family=family).fit()
    df_effect = pd.DataFrame(np.exp(model_poisson_in.params), columns=['Effect']) #, dtypes = {'Effect': int})

    df_effect.loc['MAE']= mean_absolute_error(y_test, model_poisson_in.predict(X_test))
    df_effect.loc['BIC']= model_poisson_in.bic
    df_effect.loc['AIC']= model_poisson_in.aic
    df_effect.loc['log-like']= model_poisson_in.llf

    forecast = model_poisson_in.predict(X_test)
    forecast = forecast.rename('Poisson')

    return model_poisson_in, df_effect, forecast

def fit_arima_model(pipe_in, features, target):

  # Get relevant columns
    df_train, df_test = pipe_in.get_train_test_split(split_date=time_split)
    mod_features = pipe_in.get_relevant_columns(features, target)

    X_train = df_train[mod_features]
    y_train = df_train[target]
    X_test = df_test[mod_features]
    y_test = df_test[target]
  
    model = auto_arima(y_train, X = X_train,
                   start_p=0, start_q=0,
                   max_p=2, max_q=2,
                   seasonal=False,
                   information_criterion='bic',
                   d=None,
                   trace=True,
                   enforce_stationarity=True,
                   error_action='ignore',
                   stepwise=True,
                   suppress_warnings=True)

    forecast = model.predict(n_periods=len(X_test), X = X_test)
    forecast = forecast.rename('ARIMA')

    df_effect = pd.DataFrame(model.params(), columns=['Effect'])
    df_effect.loc['MAE']= mean_absolute_error(y_test, forecast)
    df_effect.loc['BIC']= model.bic()
    df_effect.loc['AIC']= model.aic()

    return model, df_effect, forecast
# %%
def cv_ml_model(pipe_in, target, models_to_test, verbose = False):

    model_results = {}

    df_transformed_data = pipe_in.transformed_data

    tscv = TimeSeriesSplit(n_splits=3)

    for model_key, mod_features in models_to_test.items():
        mod_features = pipe_in.get_relevant_columns(mod_features, target)
        print(f"Training {model_key} with features {mod_features} on target {target}")

        cv = cross_validate(model_dict[model_key]
                            , df_transformed_data[mod_features]
                            , df_transformed_data[target].to_frame()
                            , cv=tscv, scoring='neg_mean_absolute_error'
                            , return_estimator=False)
        
        model_results[model_key] = cv

    if verbose:df_transformed_data.to_csv('df_transformed_data.csv')
    return model_results
def tune_ml_model(pipe_in, target, models_to_test, verbose = False):
    
    param_grids = {
    'RF': {
      'n_estimators': [100, 200, 300, 500],
      'max_depth': [5, 15, 30, 40],
    },
    # 'RF': {
    #   'n_estimators': [100],
    #   'bmax_depth': [5],
    # },
    'KNeigh': {
      'n_neighbors': [3, 5, 7, 10, 20],
      'weights': ['uniform', 'distance']
    },
    'GBR': {
      'n_estimators': [20, 50, 100, 150],
      'learning_rate': [0.01, 0.1, 0.2],
      'max_depth': [3, 4, 5]
    },
    'XGB': {
      'n_estimators': [50, 100, 150, 300]
    },
    'SVR': {
      'C': [0.1, 1, 10],
      'kernel': ['linear', 'rbf']
    },
    'LGB': {
      'num_leaves': [31, 50, 70],
      'learning_rate': [0.01, 0.05],
      'max_depth': [-1, 10, 20],
      'estimators': [100, 200, 500]
    },
    'EN' : {
    'alpha': [0.1, 1, 10, 100, 200],
    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 1]
    }
    }

    param_grids.update({i+'RC': {'base_estimator__'+j: param_grids[i][j] for j in param_grids[i]} for i in param_grids})

    model_results = {}
       
    df_transformed_data = pipe_in.transformed_data
    
    tscv = TimeSeriesSplit(n_splits=3)

    for model_key, mod_features in models_to_test.items():
        mod_features = pipe_in.get_relevant_columns(mod_features, target)
        print(f"Training {model_key} with features {mod_features}")

        # Perform grid search with cross-validation for each pipeline
        grid_search = GridSearchCV(model_dict[model_key]
                                   , param_grids[model_key]
                                   , cv=tscv
                                   , scoring='neg_mean_absolute_error'
                                   , n_jobs=-1)
        
        grid_search.fit(df_transformed_data[mod_features], df_transformed_data[target].to_frame())

        best_params_rf = grid_search.best_params_
        best_score_rf = grid_search.best_score_
        best_model_rf = grid_search.best_estimator_

        print(f"Best parameters for {model_key}: {best_params_rf}")
        print(f"Best score for {model_key}: {best_score_rf}")

        model_results[model_key] = fitted_model(target=target, predictors=mod_features, model=best_model_rf, error=best_score_rf, model_key=model_key, params=best_params_rf, cv=grid_search.cv_results_)
    
    if verbose:df_transformed_data.to_csv('df_transformed_data.csv')
    return model_results
def get_predictions(pipe_in, model_dict, models_to_test, target):
    fitted_models = {}
    dft_train, dft_test = pipe_in.get_train_test_split(split_date=time_split)

    monthly_counts = pipe_in.transformed_data.resample('M')[target].sum()

    multivariate_pred = pd.DataFrame(index=dft_test.index)                 # Initiate df to hold prediction for each model
    #multivariate_pred[target] = dft_test[target]                        # Include actual results in the df

    for model_key, mod_features in models_to_test.items():
        mod_features = pipe_in.get_relevant_columns(mod_features, target)
        current_model = model_dict[model_key]
        current_model.fit(dft_train[mod_features], dft_train[target].to_frame())
        fitted_models[model_key] = current_model
        multivariate_pred[model_key] = current_model.predict(dft_test[mod_features])
    
    multivariate_pred['mean'] = multivariate_pred.mean(axis=1) 
    multivariate_pred['std'] = multivariate_pred.std(axis=1)   
    multivariate_pred= multivariate_pred.round()

    total_pred = pd.concat([multivariate_pred.resample('M').sum()
                        , monthly_counts], axis=1)
                            
    return total_pred, fitted_models

# %% Model fitting and prediction

model_dict = {
  'EN': ElasticNet(),
  'RF': RandomForestRegressor(),
  'KNeigh': KNeighborsRegressor(),
  'GBR': GradientBoostingRegressor(),
  'XGB': xgb.XGBRegressor(),
  'SVR': SVR(),
  'LGB': LGBMRegressor()
}
model_dict.update({i+'RC' : RegressorChain(j) for i,j in model_dict.items()})

target = 'count'
categories = ['holiday', 'workingday', 'weather']
features = [col for col in df_source_raw.columns if col != target]
features.remove('month')    # Remove month as it is coded as cyclical for prediction

models_to_test = {'RF': features, 'KNeigh': features, 'GBR': features
                  , 'XGB': features, 'EN': features, 'LGB': features}

full_pipeline = pipeline(df_source_raw, categorical_encode=categories, cyclical_col={'month': 12}, lag_dict={'count': [1,6,7]})

cv_result = cv_ml_model(full_pipeline, target, models_to_test, verbose=False)
cv_result_df = pd.DataFrame([list(val['test_score']) for val in cv_result.values()], index=cv_result.keys())
cv_result_df['mean'] = cv_result_df.mean(axis=1)

a1, _, a_forecast = fit_arima_model(full_pipeline, features, target)
p1, _, p_forecast = fit_poisson_model(full_pipeline, features, target, sm.families.Poisson())

total_pred, fitted_models = get_predictions(full_pipeline, model_dict, models_to_test, target)
total_pred = total_pred.join([a_forecast.resample('M').sum(), p_forecast.resample('M').sum()])

pdf.plot_cv_results(cv_result_df)
pdf.plot_graph(total_pred)


# %% Inference section

print("Plotting SHAP values...")

features = [col for col in df_source_raw.columns if col != target]
features.remove('month')  # Remove month as it is coded as cyclical for prediction
features.remove('time_step')  # Remove time_step as it is not a an effect we are interested

inference_pipe = pipeline(df_source_raw, categorical_encode=full_pipeline.categorical_encode)

mod_features = inference_pipe.get_relevant_columns(features, target)
df_encoded_x = inference_pipe.transformed_data[mod_features]
df_encoded_y = inference_pipe.transformed_data[target]

model_shap = RandomForestRegressor(n_estimators=100, random_state=42)
model_shap.fit(df_encoded_x , df_encoded_y )

import shap
explainer_function = shap.Explainer(model_shap)
shap_values = explainer_function(df_encoded_x)

pdf.plot_beeswarm(shap_values)


#%%
# i_med = np.argsort(df_encoded_y)[len(df_encoded_y)//2]
# shap.plots.waterfall(shap_values[i_med], max_display=99, show=True)
# clustered_features = shap.utils.hclust(df_encoded_x, df_encoded_y)
# shap.plots.bar(shap_values, clustering=clustered_features)

# %%

fm = [col for col in df_source_raw.columns if col != target]
f0 = ['holiday' , 'weekday' , 'workingday' , 'weather' , 'temp' , 'feel_temp' , 'humidity' , 'windspeed']
f1 = ['holiday'             , 'workingday'             ,' temp' , 'feel_temp'              , 'windspeed']
f2 = ['holiday'             , 'workingday'                      , 'feel_temp' , 'humidity' , 'windspeed']
f3 = ['holiday'                            , 'weather' , 'temp' , 'feel_temp' , 'humidity'              ]
f4 = [                        'weekday'    , 'weather' , 'temp' , 'feel_temp'              , 'windspeed']
f5 = [                         'weekday'                                       , 'humidity'              ]
f6 = ['quarter'                                        , 'weather']

list_of_f = [fm, f0, f1, f2, f3, f4, f5, f6]

poisson_models_list = []
df_effect_poisson = pd.DataFrame()

for flist in list_of_f:
  model_poisson_out, e_b, _ = fit_poisson_model(inference_pipe, flist, target, sm.families.Poisson())
  df_effect_poisson = pd.concat([df_effect_poisson, e_b], axis=1)
  poisson_models_list.append(model_poisson_out)

#%%
arima_models_list = []
df_effect_arima = pd.DataFrame()

for flist in list_of_f:
  model_arima_out, e_b, _ = fit_arima_model(inference_pipe, flist, target)
  df_effect_arima = pd.concat([df_effect_arima, e_b], axis=1)
  arima_models_list.append(model_arima_out)

# %%
df_graph = df_effect_poisson[df_effect_poisson.index.isin(inference_pipe.get_relevant_columns(fm, target))].T



import matplotlib.pyplot as plt

df_graph.plot(kind='box', figsize=(10, 6))
plt.title('Effect of Features on Poisson Model')
plt.xlabel('Features')
plt.ylabel('Effect')
plt.show()

# %%
