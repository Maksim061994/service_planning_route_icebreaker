import pandas as pd
from tqdm import tqdm


def make_csv_by_integrety_data_for_pgsql(path_to_excel: str, path_to_csv: str) -> pd.DataFrame:
    xls = pd.ExcelFile(path_to_excel)
    lon = pd.read_excel(xls, 'lon', header=None)
    lat = pd.read_excel(xls, 'lat', header=None)
    result = []
    for sheet_name in tqdm(xls.sheet_names[2:]):
        one_week = pd.read_excel(xls, sheet_name, header=None)
        for i in range(one_week.shape[0]):
            for j in range(one_week.shape[1]):
                date = pd.to_datetime(sheet_name) + pd.to_timedelta("730 D")
                result.append((i, j, date, lon.iloc[i, j], lat.iloc[i, j], one_week.iloc[i, j]))

    df = pd.DataFrame(result, columns=["row_index", "column_index", "date", "lat", "lon", "value"])
    df.to_csv(path_to_csv, sep=";", index=False)
    return df


if __name__ == "__main__":
    make_csv_by_integrety_data_for_pgsql('data/IntegrVelocity.xlsx', 'data/IntegrVelocity.csv')
