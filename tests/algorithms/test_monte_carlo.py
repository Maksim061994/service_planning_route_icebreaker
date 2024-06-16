import numpy as np
from app.helpers.connector_pgsql import PostgresConnector
from app.workers.algorithm.monte_carlo import MonteCarlo
from app.workers.algorithm.player import Player
import pickle
import asyncio


def get_max_key(G):
    max_G_date = -np.inf
    for G_key in G.keys():
        if max_G_date < G_key[3]:
            max_G_date = G_key[3]
    return max_G_date


async def test_monte_carlo_algorithm():

    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    orders = await conn.get_data_async("select id from orders order by id")
    icebreakers = await conn.get_data_async("select id from icebreakers order by id")

    d_orders_rename = {orders[i]['id']:i for i in range(len(orders))}
    d_icebreakers_rename = {icebreakers[i]['id']: i for i in range(len(icebreakers))}


    d_orders_reverse = {i: orders[i]['id'] for i in range(len(orders))}
    d_icebreakers_reverse = {i: icebreakers[i]['id'] for i in range(len(icebreakers))}

    # Задаем количество итераций для алгоритма Монте-Карло поиска по деревьям
    number_step = 10

    number_of_icebreakers = len(icebreakers)

    # Задаем стартовую позицию ледоколов
    start_position = [27, 41, 16, 6]

    # Создаем стартовый список заявок у ледоколов (в начале игры - пустой)
    start_icebreaker_order_list = list()
    for i in range(number_of_icebreakers):
        start_icebreaker_order_list.append(list())

    # Задаем начальную дату
    start_date = np.zeros((number_of_icebreakers,))

    # Задаем начальное вознаграждение
    start_reward = 0

    with open("data/clean_orders.pickle", "rb") as fp:
        order_list = pickle.load(fp)

    for i in range(len(order_list)):
        order_list[i][3] = d_orders_rename[order_list[i][3]]

    # Загружаем словарь времени в пути между портами
    with open("data/full_graph.pickle", "rb") as fp:
        G = pickle.load(fp)

    new_G = dict()
    for k, value in G.items():
        if k[4] == 0:
            new_G[(d_orders_rename[k[0]], k[1], k[2], k[3], k[4])] = value
        elif k[4] == 1:
            new_G[(d_icebreakers_rename[k[0]], k[1], k[2], k[3], k[4])] = value
    G = new_G
    del new_G

    # Находим максимальную дату по положению льдов в словаре
    max_G_date = get_max_key(G)
    print("max_G_date:", max_G_date)
    print("order_list:", order_list)

    player = Player()
    monte_carlo_alg = MonteCarlo(
        player=player,
        number_step=number_step,
        G=G
    )

    # Запускаем алгоритм Монте-Карло
    best_try_reward, best_try_path = monte_carlo_alg.mcts(
        number_of_icebreakers=number_of_icebreakers, order_list=order_list.copy(),
        start_icebreaker_position=start_position.copy(),
        start_icebreaker_order_list=start_icebreaker_order_list.copy(),
        start_date=start_date, start_reward=start_reward, max_G_date=max_G_date,
        verbose=False
    )

    print("best_try_reward", best_try_reward)

    # Рассчитываем путь для лучшего решения, найденного алгоритмом Монте-Карло
    result_list = player.calculate_result_plan(
        actions_list=best_try_path, number_of_icebreakers=number_of_icebreakers,
        G=G, order_list=order_list.copy(), start_icebreaker_position=start_position.copy(),
        start_icebreaker_order_list=start_icebreaker_order_list.copy(),
        start_date=start_date, start_reward=start_reward, max_G_date=max_G_date
    )

    for i in range(len(result_list)):
        result_list[i][0] = d_icebreakers_reverse[result_list[i][0]]
        for j in range(len(result_list[i][2])):
            result_list[i][2][j][3] = d_orders_reverse[result_list[i][2][j][3]]

    return result_list, best_try_reward, best_try_path


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_monte_carlo_algorithm())
