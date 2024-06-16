import numpy as np
import random
import pandas as pd
import pickle
from tqdm import tqdm
from app.helpers.connector_pgsql import PostgresConnector

DEFAULT_BIG_VALUE = 10 ** 10



def calculate_best_path_by_ship_type(G, start_point, end_point, ship_type, date_otpr, max_G_date):
    dt_otpr = int((date_otpr - 96) / 24 / 7) * 24 * 7 + 96
    if dt_otpr > max_G_date:
        dt_otpr = max_G_date

    if start_point == end_point:
        return 0

    key = (ship_type[0], start_point, end_point, dt_otpr, ship_type[1])
    if start_point > end_point:
        key = (ship_type[0], end_point, start_point, dt_otpr, ship_type[1])

    if G.get(key, DEFAULT_BIG_VALUE) == DEFAULT_BIG_VALUE:
        print("ERROR! NO SUCH KEY IN DICT.", key)

    return G.get(key, DEFAULT_BIG_VALUE)


def calculate_best_path(G, start_point, end_point, icebraker_orders, ship_type, date_otpr, max_G_date):
    t = list()
    if len(icebraker_orders) == 0:
        res = calculate_best_path_by_ship_type(G, start_point, end_point, ship_type, date_otpr, max_G_date=max_G_date)
        t.append(res)
    else:
        for i in range(len(icebraker_orders)):
            res = calculate_best_path_by_ship_type(G, start_point, end_point, ship_type=(icebraker_orders[i][3], 0),
                                             date_otpr=date_otpr, max_G_date=max_G_date)
            t.append(res)
    return np.max(np.array(t))


def select_random_action_type(move):
    return random.randint(0, 1)


def best_way_to_make_2_orders(G, icebraker_position, icebraker_orders, ship_type, date_otpr, max_G_date):
    pos = icebraker_orders[0][1]
    t1 = date_otpr + calculate_best_path(G, icebraker_position, pos, icebraker_orders, ship_type, date_otpr, max_G_date)
    r1 = t1 - icebraker_orders[0][2]
    t1 += calculate_best_path_by_ship_type(G, pos, icebraker_orders[1][1], (icebraker_orders[1][3], 0), date_otpr,
                                           max_G_date)
    r1 += t1 - icebraker_orders[1][2]

    pos = icebraker_orders[1][1]
    t2 = date_otpr + calculate_best_path(G, icebraker_position, pos, icebraker_orders, ship_type, date_otpr, max_G_date)
    r2 = t2 - icebraker_orders[1][2]
    t2 += calculate_best_path_by_ship_type(G, pos, icebraker_orders[0][1], (icebraker_orders[0][3], 0), date_otpr,
                                           max_G_date)
    r2 += t2 - icebraker_orders[0][2]

    if r1 <= r2:
        return icebraker_orders[0], 0, t1, icebraker_orders[1][1], r1
    else:
        return icebraker_orders[1], 1, t2, icebraker_orders[0][1], r2


def best_way_to_make_all_orders(G, icebraker_position, icebraker_orders, ship_type, date_otpr, max_G_date):
    if len(icebraker_orders) == 1:
        t = date_otpr + calculate_best_path(G, icebraker_position, icebraker_orders[0][1], icebraker_orders, ship_type,
                                            date_otpr, max_G_date)
        r = t - icebraker_orders[0][2]
        return icebraker_orders[0], 0, t, icebraker_orders[0][1], r

    elif len(icebraker_orders) == 2:
        order, order_num, t, new_icebraker_position, r = best_way_to_make_2_orders(G, icebraker_position,
                                                                                   icebraker_orders.copy(), ship_type,
                                                                                   date_otpr, max_G_date)
        return order, order_num, t, new_icebraker_position, r

    elif len(icebraker_orders) == 3:
        t = date_otpr * np.ones((len(icebraker_orders),))
        r = np.zeros((len(icebraker_orders),))
        new_icebraker_position = np.zeros((len(icebraker_orders),))

        for i in range(len(icebraker_orders)):
            pos = icebraker_orders[i][1]
            t[i] += calculate_best_path(G, icebraker_position, pos, icebraker_orders, ship_type, date_otpr, max_G_date)
            r[i] = t[i] - icebraker_orders[i][2]
            new_orders = icebraker_orders.copy()
            new_orders.pop(i)

            _, _, spent_time, new_pos, rw = best_way_to_make_2_orders(G, pos, new_orders.copy(), ship_type, date_otpr,
                                                                      max_G_date)

            t[i] += spent_time
            r[i] += rw
            new_icebraker_position[i] = new_pos
        order_num = np.argmin(r)
        order = icebraker_orders[order_num]
        return order, order_num, t[order_num], new_icebraker_position[order_num], r[order_num]

    else:
        print("ERROR! ICEBRAKER HAS NO ORDER")
        return np.nan, np.nan, np.nan, np.nan, np.nan


# Action - выбор действия
# Эпсилон-жадная стратегия поведения игрока в неисследованных узлах дерева
def playout_strategy(G, move, epsilon, icebraker_position, order_list, icebraker_orders, ship_type, date, max_G_date):
    # Выбираем следующий шаг случайным образом в соответствии с эпсилон-жадным алгоритмом
    if random.uniform(0, 1) < epsilon:

        # Учитываем условие, что длина каравана составляет не более 3 кораблей помимо ледокола
        if len(icebraker_orders) == 0:
            action_type = 0
            order_num = random.randint(0, len(order_list) - 1)
            take_order = order_list[order_num]

        elif (len(icebraker_orders) == 1) | (len(icebraker_orders) == 2):
            if len(order_list) == 0:
                action_type = 1
                order_num = random.randint(0, len(icebraker_orders) - 1)
                take_order = icebraker_orders[order_num]
            else:
                action_type = select_random_action_type(move)
                if action_type == 0:
                    order_num = random.randint(0, len(order_list) - 1)
                    take_order = order_list[order_num]
                if action_type == 1:
                    order_num = random.randint(0, len(icebraker_orders) - 1)
                    take_order = icebraker_orders[order_num]
        else:
            action_type = 1
            order_num = random.randint(0, len(icebraker_orders) - 1)
            take_order = icebraker_orders[order_num]
        return action_type, take_order, order_num

    # Выбираем следующий шаг в соответствии с некоторым "разумным" алгоритмом
    else:
        if len(icebraker_orders) == 0:
            l = np.zeros((len(order_list),))
            for i in range(len(order_list)):
                time_to_go = calculate_best_path(G, icebraker_position, order_list[i][0], icebraker_orders, ship_type, date, max_G_date)
                l[i] = np.max([date + time_to_go, order_list[i][2]])
            action_type = 0
            num_order_in_list = np.argmin(l)
            order = order_list[num_order_in_list]
            return action_type, order, num_order_in_list

        elif (len(order_list) == 0) | (len(icebraker_orders) > 2):
            order, num_order_in_list, _, _, _ = best_way_to_make_all_orders(G, icebraker_position,
                                                                            icebraker_orders.copy(), ship_type, date,
                                                                            max_G_date)
            action_type = 1
            return action_type, order, num_order_in_list

        else:
            l = np.zeros((len(order_list), 2))

            for i in range(len(order_list)):
                time_to_go = calculate_best_path(G, icebraker_position, order_list[i][0], icebraker_orders, ship_type,
                                                 date, max_G_date)
                new_date = np.max([date + time_to_go, order_list[i][2]])
                new_orders = icebraker_orders.copy()
                new_orders.append(order_list[i])
                _, _, _, _, dr = best_way_to_make_all_orders(G, order_list[i][0], new_orders.copy(), ship_type,
                                                             new_date, max_G_date)
                l[i, 0] = dr

            ox, n_ox, st, new_icebreaker_position, sr = best_way_to_make_all_orders(G, icebraker_position,
                                                                                    icebraker_orders.copy(), ship_type,
                                                                                    date, max_G_date)
            for i in range(len(order_list)):
                l[i, 1] += sr
                time_to_go = calculate_best_path(G, new_icebreaker_position, order_list[i][0], icebraker_orders,
                                                 ship_type, st, max_G_date)
                new_date = np.max([st + time_to_go, order_list[i][2]])

                wt = calculate_best_path(G, order_list[i][0], order_list[i][1], [order_list[i]], ship_type, new_date,
                                         max_G_date)
                l[i, 1] += new_date + wt - order_list[i][2]

            idx, action_type = np.unravel_index(np.argmin(l), l.shape)

            if action_type == 0:
                return action_type, order_list[idx], idx
            if action_type == 1:
                return action_type, ox, n_ox


def take_order_function(G, take_order, order_num, order_list, icebraker_orders, icebraker_position, ship_type, date,
                        max_G_date):
    icebraker_orders.append(take_order)
    # Находим пункт отправления из заявки
    end_pos = take_order[0]
    # Считаем время в пути по оптимальному маршруту в зависимости от характеристик судов в караване
    time_to_go = calculate_best_path(G, icebraker_position, end_pos, icebraker_orders, ship_type, date, max_G_date)
    # Находим дату по окончании данного маршрута, причем, если дата отправления в зявки больше даты прибытия в пункт отправления ледокола,
    # то берем ее (т.е. таким образом ледокол ждет отправления судна)
    date = np.max([date + time_to_go, take_order[2]])
    # Изменяем позицию корабля в следующем состоянии - он приплывет в пункт отправления из заявки
    icebraker_position = end_pos
    # Удаляем взятую заявку из общего перечня
    order_list.pop(order_num)

    return order_list.copy(), icebraker_orders.copy(), icebraker_position, date


def make_order_function(G, take_order, order_num, order_list, icebraker_orders, icebraker_position, ship_type, date,
                        max_G_date):
    # Находим пункт назначения из заявки
    end_pos = take_order[1]
    # Считаем время в пути по оптимальному маршруту в зависимости от характеристик судов в караване
    time_to_go = calculate_best_path(G, icebraker_position, end_pos, icebraker_orders, ship_type, date, max_G_date)
    # Находим дату по окончании данного маршрута
    date += time_to_go
    # Изменяем позицию корабля в следующем состоянии - он приплывет в пункт назначения из заявки
    icebraker_position = end_pos
    # Удаляем выполненную заявку
    icebraker_orders.pop(order_num)

    return order_list.copy(), icebraker_orders.copy(), icebraker_position, date


def play_episode(G, number_of_icebrakers, order_list, epsilon, start_icebraker_position, start_icebraker_order_list,
                 start_date, start_reward, max_G_date, print_results=True):
    icebraker_orders = start_icebraker_order_list
    icebraker_position = start_icebraker_position

    move = 0
    reward = start_reward
    list_of_actions = list()

    icebrakers_next_move = np.zeros((number_of_icebrakers, 2))
    icebrakers_next_move[:, 0] = np.arange(number_of_icebrakers)
    icebrakers_next_move[:, 1] = start_date
    icebrakers_next_move = pd.DataFrame(icebrakers_next_move)
    icebrakers_next_move.columns = ["icebraker_number", "next_move_time"]

    while len(order_list) + sum([len(w) for w in icebraker_orders]) > 0:
        if print_results == True:
            print('move:', move)
            print('total_orders:', order_list)
            print('icebraker_orders:', icebraker_orders)
            print('icebraker_position:', icebraker_position)

        # Сортируем по дате, берем ближайший по дате действия ледокол
        icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
        date = icebrakers_next_move.next_move_time.iloc[0]
        icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
        ship_type = (icebraker_to_move, 1)

        if (len(order_list) == 0) & (len(icebraker_orders[icebraker_to_move]) == 0):
            icebrakers_next_move.next_move_time.iloc[0] = np.inf
            continue

        if print_results == True:
            print('date:', date)
            print('icebraker_to_move:', icebraker_to_move)
            print('icebrakers_next_move:', icebrakers_next_move)
            # Action - выбор действия в соответствии с эпсилон-жадной стратегией
        # action_type = 0 - берем заявку, action_type = 1 - исполняем заявку
        action_type, take_order, order_num = playout_strategy(G, move, epsilon, icebraker_position[icebraker_to_move],
                                                              order_list.copy(),
                                                              icebraker_orders[icebraker_to_move].copy(),
                                                              ship_type, date, max_G_date)
        list_of_actions.append([action_type, order_num])

        if action_type == 0:
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = take_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)
        if action_type == 1:
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = make_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)
            # Рассчитываем суммарную награду как разность текущей даты и желаемой даты начала плавания корабля из заявки
            reward += icebrakers_next_move.next_move_time.iloc[0] - take_order[2]

            # Переходим к следующему ходу в игре
        move += 1
        if print_results == True:
            print('action_type:', action_type)
            print('take_order:', take_order, 'order_num:', order_num)
            print('icebraker_orders:', icebraker_orders)
            print('date:', date)
            print('reward:', reward)
            print(30 * '---')

    return -reward, list_of_actions


def play_actions(actions_list, number_of_icebrakers, G, order_list, start_icebraker_position,
                 start_icebraker_order_list, start_date, start_reward, max_G_date, print_results=False):
    icebraker_orders = start_icebraker_order_list
    icebraker_position = start_icebraker_position
    date = start_date
    move = 0
    reward = start_reward

    icebrakers_next_move = np.zeros((number_of_icebrakers, 2))
    icebrakers_next_move[:, 0] = np.arange(number_of_icebrakers)
    icebrakers_next_move[:, 1] = start_date
    icebrakers_next_move = pd.DataFrame(icebrakers_next_move)
    icebrakers_next_move.columns = ["icebraker_number", "next_move_time"]
    icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
    icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
    ship_type = (icebraker_to_move, 1)

    if print_results == True:
        print('actions_list:', actions_list)
        print('order_list:', order_list)
        print('icebraker_orders:', icebraker_orders)
        print('icebraker_position:', icebraker_position)
        print('date:', date)
        print('reward:', reward)
        print(30 * '---')

    for i in range(len(actions_list)):
        # Сортируем по дате, берем ближайший по дате действия ледокол
        icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
        date = icebrakers_next_move.next_move_time.iloc[0]
        icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
        ship_type = (icebraker_to_move, 1)

        while len(order_list) + len(icebraker_orders[icebraker_to_move]) <= 0:
            icebrakers_next_move.next_move_time.iloc[0] = np.inf
            icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
            date = icebrakers_next_move.next_move_time.iloc[0]
            icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
            ship_type = (icebraker_to_move, 1)

        action_type, order_num = actions_list[i]

        if action_type == 0:
            take_order = order_list[order_num]
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = take_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)
        if action_type == 1:
            take_order = icebraker_orders[icebraker_to_move][order_num]
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = make_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)
            reward += icebrakers_next_move.next_move_time.iloc[0] - take_order[2]

            # Переходим к следующему ходу в игре
        move += 1

        if print_results == True:
            print('icebrakers_next_move:', icebrakers_next_move)
            print('icebraker_to_move:', icebraker_to_move)
            print('date:', date)
            print('action_type:', action_type)
            print('take_order:', take_order, 'order_num:', order_num)
            print('order_list:', order_list)
            print('icebraker_orders:', icebraker_orders)
            print('icebraker_position:', icebraker_position)
            print('date:', date)
            print('reward:', reward)
            print(30 * '---')

    possible_actions_list = list()
    icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
    icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])

    if len(icebraker_orders[icebraker_to_move]) == 0:
        possible_action_type = 0
        for i in range(len(order_list)):
            possible_actions_list.append([possible_action_type, i])
    elif len(icebraker_orders[icebraker_to_move]) > 2:
        possible_action_type = 1
        for i in range(len(icebraker_orders[icebraker_to_move])):
            possible_actions_list.append([possible_action_type, i])
    else:
        possible_action_type = 0
        for i in range(len(order_list)):
            possible_actions_list.append([possible_action_type, i])
        possible_action_type = 1
        for i in range(len(icebraker_orders[icebraker_to_move])):
            possible_actions_list.append([possible_action_type, i])

    icebrakers_next_move = icebrakers_next_move.sort_values(by=["icebraker_number"])
    dt_date = np.array(icebrakers_next_move.next_move_time)

    return -reward, order_list, icebraker_orders, icebraker_position, dt_date, move, possible_actions_list


def calculate_path(actions_list, number_of_icebrakers, G, order_list, start_icebraker_position,
                   start_icebraker_order_list, start_date, start_reward, max_G_date, print_results=False):
    icebraker_orders = start_icebraker_order_list
    icebraker_position = start_icebraker_position
    date = start_date
    move = 0
    reward = start_reward

    result_list = list()

    icebrakers_next_move = np.zeros((number_of_icebrakers, 2))
    icebrakers_next_move[:, 0] = np.arange(number_of_icebrakers)
    icebrakers_next_move[:, 1] = start_date
    icebrakers_next_move = pd.DataFrame(icebrakers_next_move)
    icebrakers_next_move.columns = ["icebraker_number", "next_move_time"]
    icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
    icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])

    if print_results == True:
        print('actions_list:', actions_list)
        print('order_list:', order_list)
        print('icebraker_orders:', icebraker_orders)
        print('icebraker_position:', icebraker_position)
        print('date:', date)
        print('reward:', reward)
        print(30 * '---')

    for i in range(len(actions_list)):
        # Сортируем по дате, берем ближайший по дате действия ледокол
        icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
        date = icebrakers_next_move.next_move_time.iloc[0]
        icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
        ship_type = (icebraker_to_move, 1)

        while len(order_list) + len(icebraker_orders[icebraker_to_move]) <= 0:
            icebrakers_next_move.next_move_time.iloc[0] = np.inf
            icebrakers_next_move = icebrakers_next_move.sort_values(by=['next_move_time', "icebraker_number"])
            date = icebrakers_next_move.next_move_time.iloc[0]
            icebraker_to_move = int(icebrakers_next_move.icebraker_number.iloc[0])
            ship_type = (icebraker_to_move, 1)

        action_type, order_num = actions_list[i]

        result_list.append(
            [icebraker_to_move, action_type, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move],
             0, icebrakers_next_move.next_move_time.iloc[0], 0])

        if action_type == 0:
            take_order = order_list[order_num]
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = take_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)

        if action_type == 1:
            take_order = icebraker_orders[icebraker_to_move][order_num]
            order_list, icebraker_orders[icebraker_to_move], icebraker_position[icebraker_to_move], \
            icebrakers_next_move.next_move_time.iloc[0] = make_order_function(G, take_order, order_num,
                                                                              order_list.copy(), icebraker_orders[
                                                                                  icebraker_to_move].copy(),
                                                                              icebraker_position[icebraker_to_move],
                                                                              ship_type, date, max_G_date)
            reward += icebrakers_next_move.next_move_time.iloc[0] - take_order[2]

        result_list[-1][4] = icebraker_position[icebraker_to_move]
        result_list[-1][6] = icebrakers_next_move.next_move_time.iloc[0]

        # Переходим к следующему ходу в игре
        move += 1

        if print_results == True:
            print('icebrakers_next_move:', icebrakers_next_move)
            print('icebraker_to_move:', icebraker_to_move)
            print('date:', date)
            print('action_type:', action_type)
            print('take_order:', take_order, 'order_num:', order_num)
            print('order_list:', order_list)
            print('icebraker_orders:', icebraker_orders)
            print('icebraker_position:', icebraker_position)
            print('date:', date)
            print('reward:', reward)
            print(30 * '---')

    return result_list


def get_max_key(G):
    max_G_date = -np.inf
    for G_key in G.keys():
        if max_G_date < G_key[3]:
            max_G_date = G_key[3]
    return max_G_date


class Node:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.childs = list()
        self.action = list()
        self.mean_value = 0.0
        self.max_value = -np.inf
        self.sum_squared_results = 0.0
        self.number_of_visits = 0.0
        self.end_node = False

    def AppendChild(self, child):
        self.childs.append(child)
        child.parent = self


def mcts(number_of_nodes_to_expanse, G, C, D, T, W, eps, number_of_icebrakers, order_list, start_icebraker_position,
         start_icebraker_order_list, start_date, start_reward, max_G_date, verbose=False):
    root_node = Node('root')

    for node_to_expanse in tqdm(range(number_of_nodes_to_expanse)):

        # Selection strategy
        node = root_node
        isSelected = False
        while len(node.childs) > 0:
            # Если дошли до конечной ноды, заканчиваем поиск
            if node.end_node == True:
                break

                # Если у ноды есть ребенок, у которых не было ни одного посещения, выбираем его
            for i in range(len(node.childs)):
                if node.childs[i].number_of_visits == 0:
                    node = node.childs[i]
                    isSelected = True
                    break

            if isSelected == True:
                break

            # Если у всех детей были посещения, движемся дальше
            # Если общее количество ноды меньше константы Т, осуществяем выбор ребенка случайным образом
            if node.number_of_visits <= T:
                if len(node.childs) > 0:
                    node = random.choice(node.childs)

            # Иначе выбираем ребенка по методу UCB
            else:
                ucb_array = np.zeros((len(node.childs),))
                for i in range(len(node.childs)):
                    v = node.childs[i].mean_value + W * node.childs[i].max_value
                    s1 = np.log(node.number_of_visits) / node.childs[i].number_of_visits
                    s2 = (node.childs[i].sum_squared_results + node.childs[i].number_of_visits * v ** 2 + D) / \
                         node.childs[i].number_of_visits
                    ucb_array[i] = v - C * s1 ** 0.5 - s2 ** 0.5
                selected_node = np.argmax(ucb_array)
                node = node.childs[selected_node]

        if node.end_node == True:
            break

            # Play-Out strategy
        # Находим путь до узла по предыдущим действиям начиная со стартового положения
        a_node = node
        actions_list = list()
        for i in range(number_of_nodes_to_expanse):
            if (not a_node.parent) == True:
                break
            else:
                actions_list.append(a_node.action)
                a_node = a_node.parent

        actions_list = actions_list[::-1]

        played_reward, played_order_list, played_icebraker_orders, played_icebraker_position, played_date, played_move, _ = play_actions(
            actions_list=actions_list.copy(),
            number_of_icebrakers=number_of_icebrakers,
            G=G,
            order_list=order_list.copy(),
            start_icebraker_position=start_icebraker_position.copy(),
            start_icebraker_order_list=start_icebraker_order_list.copy(),
            start_date=start_date.copy(),
            start_reward=start_reward,
            max_G_date=max_G_date)

        new_reward, new_list_of_actions = play_episode(G=G,
                                                       epsilon=eps,
                                                       number_of_icebrakers=number_of_icebrakers,
                                                       order_list=played_order_list.copy(),
                                                       start_icebraker_position=played_icebraker_position.copy(),
                                                       start_icebraker_order_list=played_icebraker_orders.copy(),
                                                       start_date=played_date.copy(),
                                                       start_reward=-played_reward,
                                                       max_G_date=max_G_date,
                                                       print_results=False)

        # Expansion strategy
        a_node = node
        a_list = actions_list.copy()
        for i in range(len(new_list_of_actions)):
            if len(a_node.childs) == 0:
                _, _, _, _, _, _, possible_actions_list = play_actions(
                    actions_list=a_list.copy(),
                    number_of_icebrakers=number_of_icebrakers,
                    G=G,
                    order_list=order_list.copy(),
                    start_icebraker_position=start_icebraker_position.copy(),
                    start_icebraker_order_list=start_icebraker_order_list.copy(),
                    start_date=start_date.copy(),
                    start_reward=start_reward,
                    max_G_date=max_G_date)

                for j in range(len(possible_actions_list)):
                    child = Node(f'child_{a_node.name}_{j}')
                    child.parent = a_node
                    child.action = possible_actions_list[j]

                    # Вписываем полученный результат симуляции в созданную child-node с соответствующим действием (т.е. первое действие симуляции)
                    if possible_actions_list[j] == new_list_of_actions[0]:
                        child.mean_value = new_reward
                        child.max_value = new_reward
                        child.sum_squared_results = new_reward ** 2
                        child.number_of_visits = 1.0

                    a_node.AppendChild(child)
                break
            else:
                child_actions = list()
                for j in range(len(a_node.childs)):
                    child_actions.append(a_node.childs[j].action)

                if new_list_of_actions[i] in child_actions:
                    idx = child_actions.index(new_list_of_actions[i])
                    a_list.append(a_node.childs[idx].action)
                    a_node = a_node.childs[idx]
                else:
                    print(vars(a_node))
                    print(new_list_of_actions[i], child_actions)
                    print("ERROR: NO CHILD WITH SAME ACTION!")

        # Backpropagation strategy
        a_node = node
        for i in range(len(actions_list)):
            a_node.mean_value = (a_node.mean_value * a_node.number_of_visits + new_reward) / (
                        a_node.number_of_visits + 1)
            a_node.sum_squared_results += new_reward ** 2
            a_node.number_of_visits += 1
            if new_reward > a_node.max_value:
                a_node.max_value = new_reward
                # Переходим на уровень выше
            a_node = a_node.parent
        if verbose == True:
            if node_to_expanse % 100 == 0:
                print("step:", node_to_expanse, "best_reward:", root_node.max_value)
                # Обновление значений в root Node и пути до лучшей попытки
        root_node.mean_value = (root_node.mean_value * root_node.number_of_visits + new_reward) / (
                    root_node.number_of_visits + 1)
        root_node.sum_squared_results += new_reward ** 2
        root_node.number_of_visits += 1
        if new_reward > root_node.max_value:
            root_node.max_value = new_reward
            root_node.end_node = actions_list + new_list_of_actions

            # Taking best try after stopping MCTS
    best_try_reward = root_node.max_value
    best_try_path = root_node.end_node

    return best_try_reward, best_try_path


async def main():
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
    number_of_nodes_to_expanse = 10

    # Задаем константы для алгоритма Монте-Карло поиска по деревьям
    C = 0.5
    D = 10000
    T = 10
    W = 0.8
    eps = 0.03

    number_of_icebrakers = 4

    # Задаем стартовую позицию ледоколов
    start_position = [27, 41, 16, 6]

    # Создаем стартовый список заявок у ледоколов (в начале игры - пустой)
    start_icebraker_order_list = list()
    for i in range(number_of_icebrakers):
        start_icebraker_order_list.append(list())

    # Задаем начальную дату
    start_date = np.zeros((number_of_icebrakers,))

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

    # Удаляем заявки с недостижимыми вершинами графа
    print("order_list:", order_list)

    count_time = 0
    for i in range(len(order_list)):
        count_time += calculate_best_path_by_ship_type(G,
                                                       start_point=order_list[i][0],
                                                       end_point=order_list[i][1],
                                                       ship_type=(order_list[i][3], 0),
                                                       date_otpr=order_list[i][2],
                                                       max_G_date=max_G_date
                                                       )
    print("count_time:", count_time)

    # Запускаем алгоритм Монте-Карло
    best_try_reward, best_try_path = mcts(number_of_nodes_to_expanse=number_of_nodes_to_expanse,
                                          G=G,
                                          C=C,
                                          D=D,
                                          T=T,
                                          W=W,
                                          eps=eps,
                                          number_of_icebrakers=number_of_icebrakers,
                                          order_list=order_list.copy(),
                                          start_icebraker_position=start_position.copy(),
                                          start_icebraker_order_list=start_icebraker_order_list.copy(),
                                          start_date=start_date,
                                          start_reward=start_reward,
                                          max_G_date=max_G_date,
                                          verbose=True)

    print("best_try_reward", best_try_reward)

    # Рассчитываем путь для лучшего решения, найденного алгоритмом Монте-Карло
    result_list = calculate_path(actions_list=best_try_path,
                                 number_of_icebrakers=number_of_icebrakers,
                                 G=G,
                                 order_list=order_list.copy(),
                                 start_icebraker_position=start_position.copy(),
                                 start_icebraker_order_list=start_icebraker_order_list.copy(),
                                 start_date=start_date,
                                 start_reward=start_reward,
                                 max_G_date=max_G_date,
                                 print_results=False)

    for i in range(len(result_list)):
        result_list[i][0] = d_icebreakers_reverse[result_list[i][0]]
        for j in range(len(result_list[i][2])):
            result_list[i][2][j][3] = d_orders_reverse[result_list[i][2][j][3]]
    return result_list, best_try_reward, best_try_path


if __name__ == "__main__":
    import asyncio
    result_list, best_try_reward, best_try_path =  asyncio.run(main())
    print(result_list, best_try_reward, best_try_path)