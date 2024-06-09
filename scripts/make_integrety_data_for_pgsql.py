import pandas as pd


def make_csv_by_integrety_data_for_pgsql(path_to_excel: str, path_to_csv: str) -> pd.DataFrame:
    xls = pd.ExcelFile(path_to_excel)
    lon = pd.read_excel(xls, 'lon', header=None)
    lat = pd.read_excel(xls, 'lat', header=None)
    result = []
    for sheet_name in xls.sheet_names[2:]:
        one_week = pd.read_excel(xls, sheet_name, header=None)
        for i in range(one_week.shape[0]):
            for j in range(one_week.shape[1]):
                result.append((sheet_name, lon.iloc[i, j], lat.iloc[i, j], one_week.iloc[i, j]))

    df = pd.DataFrame(result, columns=["date", "lat", "lon", "value"])
    df.to_csv(path_to_csv, sep=";")
    return df


if __name__ == "__main__":
    make_csv_by_integrety_data_for_pgsql('data/IntegrVelocity.xlsx', 'data/IntegrVelocity.csv')