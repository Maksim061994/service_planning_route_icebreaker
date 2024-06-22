from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
import copy

from app.helpers.connector_pgsql import PostgresConnector
from app.workers.algorithm.monte_carlo import MonteCarlo
from app.workers.algorithm.player import Player


class CalculateScheduler:
    def __init__(self, settings):
        self.data = None
        self.dataframe = None
        self.connector = PostgresConnector(
            host=settings.db_host,
            user=settings.db_user,
            password=settings.db_password,
            dbname=settings.db_name_database,
            port=settings.db_port
        )
        self.player = Player()

    def compute_schedule(self, input_params):
        params = self.__get_params()
        params.update(input_params)
        self.params = params
        points = self.__get_points()
        orders, d_orders_rename, d_orders_reverse = self.__get_orders()
        icebreakers, d_icebreakers_rename, d_icebreakers_reverse = self.__get_icebreakers()
        number_of_icebreakers = len(icebreakers)
        start_position = self.__get_start_position_icebreakers(points, icebreakers)
        start_icebreaker_order_list = [[] for _ in range(number_of_icebreakers)]

        # Задаем начальную дату
        start_date = np.zeros((number_of_icebreakers,))

        # Задаем начальное вознаграждение
        start_reward = 0

        order_list = self.__get_clean_orders(params['date_start'], d_orders_rename)
        graph_data, max_G_date = self.__get_graph_data(params['date_start'], d_orders_rename, d_icebreakers_rename)
        import pickle
        with open("data/graph_data.pickle", "wb") as f:
            pickle.dump(graph_data, f)

        monte_carlo_alg = MonteCarlo(
            player=self.player,
            number_step=params["num_iterations"],
            G=graph_data, C=params["C_mc"],
            D=params["D_mc"], W=params["W_mc"],
            T=params["T_mc"], eps=params["eps_mc"]
        )

        # Запускаем алгоритм Монте-Карло
        best_try_reward, best_try_path = monte_carlo_alg.mcts(
            number_of_icebreakers=number_of_icebreakers, order_list=order_list.copy(),
            start_icebreaker_position=start_position.copy(),
            start_icebreaker_order_list=start_icebreaker_order_list.copy(),
            start_date=start_date, start_reward=start_reward, max_G_date=max_G_date,
            verbose=False
        )

        # Рассчитываем путь для лучшего решения, найденного алгоритмом Монте-Карло
        result_list = self.player.calculate_result_plan(
            actions_list=best_try_path, number_of_icebreakers=number_of_icebreakers,
            G=graph_data, order_list=order_list.copy(), start_icebreaker_position=start_position.copy(),
            start_icebreaker_order_list=start_icebreaker_order_list.copy(),
            start_date=start_date, start_reward=start_reward, max_G_date=max_G_date
        )

        result_list_new = self.__post_processing(copy.deepcopy(result_list), d_icebreakers_reverse, d_orders_reverse)
        self.data = result_list_new
        self.dataframe = self.__get_dataframe_with_dt()
        return best_try_reward

    def save_dataframe(self):
        if self.dataframe is None:
            raise ValueError("Dataframe is not computed")
        date_start = self.params['date_start']
        self.connector.connect()
        self.connector.execute_query(
            "DELETE FROM route_icebreakers_detail;"
        )  # TODO: костыль, который обеспичавет создание нового расписания для каждого нового запуска

        for i in range(self.dataframe.shape[0]):
            row = self.dataframe.iloc[i]
            icebreaker_id = int(row["icebreaker_id"])
            action_type = int(row["action_type"])
            nested_array_orders = row["nested_array_orders"]
            nested_array_orders_str = '{' + ','.join('{' + ','.join(map(str, inner)) + '}' for inner in nested_array_orders) + '}'
            points_start_id = int(row["points_start_id"])
            points_end_id = int(row["points_end_id"])
            datetime_work = row["datetime_work"]
            datetime_work = (date_start + pd.Timedelta(hours=datetime_work))
            hour_start = row["datetime_start"]
            hour_end = row["datetime_end"]
            date_start_new = (date_start + pd.Timedelta(hours=hour_start))
            date_end_new = (date_start + pd.Timedelta(hours=hour_end))
            count_ships = row["count_ships"]
            query = f"""
                    INSERT INTO route_icebreakers_detail (icebreaker_id, action_type, nested_array_orders, points_start_id, points_end_id, datetime_work, datetime_start, datetime_end, count_ships)
                    VALUES ({icebreaker_id}, {action_type}, '{nested_array_orders_str}', {points_start_id}, {points_end_id}, '{datetime_work}', '{date_start_new}', '{date_end_new}', {count_ships})
                """
            self.connector.execute_query(query)
        self.connector.close()

    def __get_dataframe_with_dt(self):
        df = pd.DataFrame(
            self.data,
            columns=[
                "icebreaker_id", "action_type", "nested_array_orders",
                "points_start_id", "points_end_id", "datetime_start", "datetime_end"
            ]
        )
        df["datetime_start_hour"] = df.datetime_start.astype(int)
        df["datetime_end_hour"] = df.datetime_end.astype(int)
        df["count_ships"] = df.nested_array_orders.apply(lambda x: len(x))
        min_hour = int(df.datetime_start_hour.min())
        max_hour = int(df.datetime_end_hour.max()) + 1
        date_range = pd.DataFrame(range(min_hour, max_hour), columns=["datetime_work"])
        output_df = []
        for ic in df.icebreaker_id.unique():
            ic_df = df[df.icebreaker_id == ic]
            res_df = date_range.merge(ic_df, how="left", left_on=["datetime_work"], right_on=["datetime_start_hour"])
            res_df = res_df.ffill().bfill()
            output_df.append(res_df)
        return pd.concat(output_df).reset_index(drop=True)

    def save_results(self):
        """
        Сохранение результатов в базу данных
        :return:
        """
        if self.data is None:
            raise ValueError("Data is not computed")
        date_start = self.params['date_start']
        self.connector.connect()
        self.connector.execute_query(
            "DELETE FROM route_icebreakers;"
        )  # TODO: костыль, который обеспичавет создание нового расписания для каждого нового запуска
        for i in range(len(self.data)):
            row = self.data[i]
            hour_start = row[5]
            hour_end = row[6]
            duration_hours = hour_end - hour_start
            date_start_new = (date_start + pd.Timedelta(hours=hour_start))
            date_end_new = (date_start + pd.Timedelta(hours=hour_end))
            order_ids = [r[-1] for r in row[2]]
            order_ids_str = '{' + ','.join(map(str, order_ids)) + '}'

            nested_array_orders_str = '{' + ','.join( '{' + ','.join(map(str, inner)) + '}' for inner in row[2]) + '}'
            query = f"""
                INSERT INTO route_icebreakers (icebreaker_id, action_type, nested_array_orders, order_ids,  points_start_id, points_end_id, datetime_start, datetime_end, duration_hours)
                VALUES ({row[0]}, {row[1]}, '{nested_array_orders_str}', '{order_ids_str}', {row[3]}, '{row[4]}', '{date_start_new}', '{date_end_new}', {duration_hours})
            """
            self.connector.execute_query(query)
        self.connector.close()

    def __post_processing(self, result_list, d_icebreakers_reverse, d_orders_reverse) -> List:
        new_list = []
        for i in range(len(result_list)):
            row = copy.deepcopy(result_list[i])
            row[0] = d_icebreakers_reverse[result_list[i][0]]
            for j in range(len(row[2])):
                row[2][j][3] = d_orders_reverse[row[2][j][3]]
            new_list.append(row)
        return new_list

    def __get_graph_data(self, date_start, d_orders_rename, d_icebreakers_rename) -> Tuple:
        self.connector.connect()
        cursor = self.connector.get_sync_cursor("select * from graph_ships order by order_id")
        column_names = [desc[0] for desc in cursor.description]
        graph = dict()
        max_G_date = -np.inf
        while True:
            graph_data = cursor.fetchmany(1000)
            if not graph_data:
                break
            for row in graph_data:
                row = dict(zip(column_names, row))
                datetime = round((row["datetime"] - date_start).total_seconds() / 3600)
                value = row["time_swim"]
                if row["type"] == 0:
                    graph[(d_orders_rename[row["order_id"]], row["points_start_id"], row["points_end_id"], datetime, 0)] = value
                elif row["type"] == 1:
                    graph[(d_icebreakers_rename[row["order_id"]], row["points_start_id"], row["points_end_id"], datetime, 1)] = value
                if max_G_date < datetime:
                    max_G_date = datetime
        self.connector.close()
        return graph, max_G_date

    def __get_clean_orders(self, date_start, d_orders_rename):
        self.connector.connect()
        orders = self.connector.get_data_sync(
            """
            select 
                point_start_id_icebreaker, point_end_id_icebreaker, 
                date_start_swim, order_id 
            from route_orders order by order_id
            """
        )
        self.connector.close()
        order_list = []
        for order in orders:
            order_id = d_orders_rename[order["order_id"]]
            date_start_swim = round((pd.to_datetime(order["date_start_swim"]) - date_start).total_seconds() / 3600)
            order_list.append([order["point_start_id_icebreaker"], order["point_end_id_icebreaker"], date_start_swim, order_id])
        return order_list

    def __get_start_position_icebreakers(self, points: List, icebreakers: List) -> List[int]:
        start_position = []
        for icebreaker in icebreakers:
            for point in points:
                if icebreaker['start_position'] == point['point_name']:
                    start_position.append(point['id'])
                    break
        return start_position

    def __get_params(self) -> Dict:
        self.connector.connect()
        params = self.connector.get_data_sync("select * from parameters")
        self.connector.close()
        p = dict()
        for r in params:
            if r['type'] == 'date':
                p[r['name']] = pd.to_datetime(r['value'])
            else:
                f = eval(r['type'])
                p[r['name']] = f(r['value'])
        return p

    def __get_points(self) -> List:
        self.connector.connect()
        points = self.connector.get_data_sync("select * from points")
        self.connector.close()
        return points

    def __get_icebreakers(self) -> Tuple:
        self.connector.connect()
        icebreakers = self.connector.get_data_sync("select * from icebreakers order by id")
        self.connector.close()
        d_icebreakers_rename = {icebreakers[i]['id']: i for i in range(len(icebreakers))}
        d_icebreakers_reverse = {i: icebreakers[i]['id'] for i in range(len(icebreakers))}
        return icebreakers, d_icebreakers_rename, d_icebreakers_reverse

    def __get_orders(self) -> Tuple:
        self.connector.connect()
        orders = self.connector.get_data_sync("select * from orders order by id")
        self.connector.close()
        d_orders_rename = {orders[i]['id']: i for i in range(len(orders))}
        d_orders_reverse = {i: orders[i]['id'] for i in range(len(orders))}
        return orders, d_orders_rename, d_orders_reverse
