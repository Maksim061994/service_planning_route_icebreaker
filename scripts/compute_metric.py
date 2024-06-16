import pandas as pd
from app.helpers.connector_pgsql import PostgresConnector


def compute_metrics():
    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    route_orders = conn.get_data_sync("select * from route_orders")
    route_icebreakers = conn.get_data_sync("select * from route_icebreakers")
    conn.close()

    result_metric = 0
    self_swim = 0
    wait_time = 0
    for order in route_orders:
        time_swim_self = order["time_swim_self"]
        result_metric += time_swim_self
        self_swim += time_swim_self

        date_start_swim = order["date_start_swim"]
        use_icebreakers = []
        for icebreaker in route_icebreakers:
            ic_orders = [ic_order[-1] for ic_order in icebreaker["nested_array_orders"]]
            if order["order_id"] in ic_orders:
                use_icebreakers.append(icebreaker)
        if len(use_icebreakers):
            if len(use_icebreakers) == 1:
                use_icebreaker = use_icebreakers[0]
                datetime_start_work_icebreaker = use_icebreaker["datetime_start"]
                time_wait_icebreaker = (datetime_start_work_icebreaker - pd.to_datetime(date_start_swim)).total_seconds() / 3600
                if time_wait_icebreaker < 0:
                    print(time_wait_icebreaker)
                time_work_icebreaker = use_icebreaker["duration_hours"]
                result_metric += (time_work_icebreaker + time_wait_icebreaker)
                wait_time += time_wait_icebreaker
            else:
                datetime_start_work_icebreaker = None
                for use_icebreaker in use_icebreakers:
                    if use_icebreaker["points_start_id"] == order["point_start_id_icebreaker"]:
                        datetime_start_work_icebreaker = use_icebreaker["datetime_start"]
                        break
                if datetime_start_work_icebreaker is None:
                    datetime_start_work_icebreaker = max([use_icebreaker["datetime_start"] for use_icebreaker in use_icebreakers])
                time_work_icebreaker = sum([use_icebreaker["duration_hours"] for use_icebreaker in use_icebreakers])
                time_wait_icebreaker = (datetime_start_work_icebreaker - pd.to_datetime(
                    date_start_swim)).total_seconds() / 3600
                if time_wait_icebreaker < 0:
                    print(time_wait_icebreaker)
                result_metric += (time_work_icebreaker + time_wait_icebreaker)
                wait_time += time_wait_icebreaker
    return result_metric, self_swim, wait_time


if __name__ == "__main__":
    result_metric = compute_metrics()
    print(result_metric)
