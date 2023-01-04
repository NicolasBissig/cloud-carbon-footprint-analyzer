import pandas as pd
import requests

def request_estimates(start: str, end: str, ignore_cache = "false", group_by = "day", base_url = "http://localhost:4000/api") -> pd.DataFrame:
    url = f'{base_url}/footprint?start={start}&end={end}&ignoreCache={ignore_cache}&groupBy={group_by}&limit=50000&skip=0'
    response = requests.get(url)
    response.raise_for_status()
    return load_estimates(response.text)

def load_estimates(path_or_raw: str, raw = False) -> pd.DataFrame: 
    raw_estimates = pd.read_json(path_or_raw)

    if raw:
        return raw_estimates
    
    return prepare_estimates(raw_estimates)

def prepare_estimates(estimates: pd.DataFrame) -> pd.DataFrame:
    exploded = estimates.explode('serviceEstimates', ignore_index=True)
    normalized = exploded.join(pd.json_normalize(exploded['serviceEstimates']))
    normalized = normalized.drop('serviceEstimates', axis='columns')
    return normalized

def unique_values_per_colum(estimates: pd.DataFrame) -> pd.DataFrame:
    unique = []
    for column in estimates.columns.tolist():
        values = estimates[column].unique()
        unique.append([column, values.size, values])

    unique_count = pd.DataFrame(unique, columns=['column', 'unique count', 'values'])
    unique_count = unique_count.sort_values(by=['unique count'], ascending=True)
    return unique_count

def sum_columns(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(df.sum(axis=0, numeric_only=True))

def sum_per_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    summed = df.groupby([column]).sum(numeric_only=True)
    summed = summed.sort_values(by=['kilowattHours', 'co2e', 'cost'], ascending=False)
    return summed