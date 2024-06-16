import numpy as np
import pandas as pd
from loguru import logger
import random
from app.workers.algorithm.helper.printer import (
    print_results_start, print_results_end, print_play_episode_start,
    print_play_episode_log, print_play_episode_end
)


class Player:

    DEFAULT_BIG_VALUE = 10**10

    def __init__(self):
        pass

    def __calculate_best_path_by_ship_type(self, G, start_point, end_point, ship_type, date_otpr, max_G_date):
        dt_otpr = int((date_otpr - 96) / 24 / 7) * 24 * 7 + 96
        if dt_otpr > max_G_date:
            dt_otpr = max_G_date

        if start_point == end_point:
            return 0

        key = (ship_type[0], start_point, end_point, dt_otpr, ship_type[1])
        if start_point > end_point:
            key = (ship_type[0], end_point, start_point, dt_otpr, ship_type[1])

        if G.get(key, self.DEFAULT_BIG_VALUE) == self.DEFAULT_BIG_VALUE:
            logger.warning(f"ERROR! NO SUCH KEY IN DICT. {key=}")

        return G.get(key, self.DEFAULT_BIG_VALUE)

    def __calculate_best_path(self, G, start_point, end_point, icebreaker_orders, ship_type, date_otpr, max_G_date):
        t = list()
        if len(icebreaker_orders) == 0:
            res = self.__calculate_best_path_by_ship_type(
                G, start_point, end_point, ship_type, date_otpr, max_G_date=max_G_date
            )
            t.append(res)
        else:
            for i in range(len(icebreaker_orders)):
                res = self.__calculate_best_path_by_ship_type(
                    G, start_point, end_point,
                    ship_type=(icebreaker_orders[i][3], 0), date_otpr=date_otpr, max_G_date=max_G_date
                )
                t.append(res)
        return np.max(np.array(t))

    def __make_order_function(
            self, G, take_order, order_num, order_list,
            icebreaker_orders, icebreaker_position, ship_type,
            date, max_G_date
    ):
            # Находим пункт назначения из заявки
            end_pos = take_order[1]
            # Считаем время в пути по оптимальному маршруту в зависимости от характеристик судов в караване
            time_to_go = self.__calculate_best_path(G, icebreaker_position, end_pos, icebreaker_orders, ship_type, date,
                                             max_G_date)
            # Находим дату по окончании данного маршрута
            date += time_to_go
            # Изменяем позицию корабля в следующем состоянии - он приплывет в пункт назначения из заявки
            icebreaker_position = end_pos
            # Удаляем выполненную заявку
            icebreaker_orders.pop(order_num)

            return order_list.copy(), icebreaker_orders.copy(), icebreaker_position, date

    def __take_order_function(
            self, G, take_order, order_num, order_list,
            icebreaker_orders, icebreaker_position, ship_type,
            date, max_G_date
    ):
        icebreaker_orders.append(take_order)

        # Находим пункт отправления из заявки
        end_pos = take_order[0]

        # Считаем время в пути по оптимальному маршруту в зависимости от характеристик судов в караване
        time_to_go = self.__calculate_best_path(
            G, icebreaker_position, end_pos, icebreaker_orders, ship_type, date, max_G_date
        )

        # Находим дату по окончании данного маршрута, причем, если дата отправления в зявки больше даты прибытия в пункт отправления ледокола,
        # то берем ее (т.е. таким образом ледокол ждет отправления судна)
        date = np.max([date + time_to_go, take_order[2]])

        # Изменяем позицию корабля в следующем состоянии - он приплывет в пункт отправления из заявки
        icebreaker_position = end_pos

        # Удаляем взятую заявку из общего перечня
        order_list.pop(order_num)

        return order_list.copy(), icebreaker_orders.copy(), icebreaker_position, date

    def __play_all_actions(self,
            actions_list, G, order_list, icebreaker_orders, icebreaker_position, icebreakers_next_move,
            date, reward, max_G_date, print_results=False
    ):
        take_order = -1
        move = 0
        if print_results:
            print_results_start(actions_list, order_list, icebreaker_orders, icebreaker_position, date, reward)
        for i in range(len(actions_list)):
            # Сортируем по дате, берем ближайший по дате действия ледокол
            icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
            date = icebreakers_next_move.next_move_time.iloc[0]
            icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])
            ship_type = (icebreaker_to_move, 1)

            while len(order_list) + len(icebreaker_orders[icebreaker_to_move]) <= 0:
                icebreakers_next_move.next_move_time.iloc[0] = np.inf
                icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
                date = icebreakers_next_move.next_move_time.iloc[0]
                icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])
                ship_type = (icebreaker_to_move, 1)

            action_type, order_num = actions_list[i]

            if action_type == 0:
                take_order = order_list[order_num]
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__take_order_function(
                    G=G, take_order=take_order, order_num=order_num, order_list=order_list.copy(),
                    icebreaker_orders=icebreaker_orders[icebreaker_to_move].copy(),
                    icebreaker_position=icebreaker_position[icebreaker_to_move],
                    ship_type=ship_type, date=date, max_G_date=max_G_date
                )

            if action_type == 1:
                take_order = icebreaker_orders[icebreaker_to_move][order_num]
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__make_order_function(
                    G=G, take_order=take_order, order_num=order_num, order_list=order_list.copy(),
                    icebreaker_orders=icebreaker_orders[icebreaker_to_move].copy(),
                    icebreaker_position=icebreaker_position[icebreaker_to_move], ship_type=ship_type,
                    date=date, max_G_date=max_G_date
                )
                reward += icebreakers_next_move.next_move_time.iloc[0] - take_order[2]

            # Переходим к следующему ходу в игре
            move += 1
            if print_results:
                print_results_end(
                    icebreakers_next_move, icebreaker_to_move, date, action_type, take_order,
                    order_num, order_list, icebreaker_orders, icebreaker_position, reward)
        return icebreakers_next_move, order_list, icebreaker_orders, reward, move

    @staticmethod
    def __select_random_action_type():
        return random.randint(0, 1)

    def __best_way_to_make_2_orders(self, G, icebreaker_position, icebreaker_orders, ship_type, date_otpr, max_G_date):
        pos = icebreaker_orders[0][1]
        t1 = date_otpr + self.__calculate_best_path(
            G, icebreaker_position, pos, icebreaker_orders, ship_type, date_otpr, max_G_date
        )
        r1 = t1 - icebreaker_orders[0][2]
        t1 += self.__calculate_best_path_by_ship_type(
            G, pos, icebreaker_orders[1][1], (icebreaker_orders[1][3], 0), date_otpr, max_G_date
        )
        r1 += t1 - icebreaker_orders[1][2]

        pos = icebreaker_orders[1][1]
        t2 = date_otpr + self.__calculate_best_path(
            G, icebreaker_position, pos, icebreaker_orders, ship_type, date_otpr, max_G_date
        )
        r2 = t2 - icebreaker_orders[1][2]
        t2 += self.__calculate_best_path_by_ship_type(
            G, pos, icebreaker_orders[0][1], (icebreaker_orders[0][3], 0), date_otpr, max_G_date
        )
        r2 += t2 - icebreaker_orders[0][2]

        if r1 <= r2:
            return icebreaker_orders[0], 0, t1, icebreaker_orders[1][1], r1
        return icebreaker_orders[1], 1, t2, icebreaker_orders[0][1], r2

    def __best_way_to_make_all_orders(
            self, G, icebreaker_position, icebreaker_orders, ship_type, date_otpr, max_G_date
    ):
        if len(icebreaker_orders) == 1:
            t = date_otpr + self.__calculate_best_path(
                G, icebreaker_position, icebreaker_orders[0][1], icebreaker_orders,
                ship_type, date_otpr, max_G_date
            )
            r = t - icebreaker_orders[0][2]
            return icebreaker_orders[0], 0, t, icebreaker_orders[0][1], r

        elif len(icebreaker_orders) == 2:
            order, order_num, t, new_icebreaker_position, r = self.__best_way_to_make_2_orders(
                G, icebreaker_position, icebreaker_orders.copy(), ship_type, date_otpr, max_G_date
            )
            return order, order_num, t, new_icebreaker_position, r

        elif len(icebreaker_orders) == 3:
            t = date_otpr * np.ones((len(icebreaker_orders),))
            r = np.zeros((len(icebreaker_orders),))
            new_icebreaker_position = np.zeros((len(icebreaker_orders),))

            for i in range(len(icebreaker_orders)):
                pos = icebreaker_orders[i][1]
                t[i] += self.__calculate_best_path(
                    G, icebreaker_position, pos, icebreaker_orders, ship_type, date_otpr, max_G_date
                )
                r[i] = t[i] - icebreaker_orders[i][2]
                new_orders = icebreaker_orders.copy()
                new_orders.pop(i)

                _, _, spent_time, new_pos, rw = self.__best_way_to_make_2_orders(
                    G, pos, new_orders.copy(), ship_type, date_otpr, max_G_date
                )

                t[i] += spent_time
                r[i] += rw
                new_icebreaker_position[i] = new_pos
            order_num = np.argmin(r)
            order = icebreaker_orders[order_num]
            return order, order_num, t[order_num], new_icebreaker_position[order_num], r[order_num]

        logger.warning("ERROR! ICEBREAKER HAS NO ORDER")
        return np.nan, np.nan, np.nan, np.nan, np.nan

    def __playout_strategy_player(
            self, G, epsilon, icebreaker_position, order_list,
            icebreaker_orders, ship_type, date, max_G_date
    ):
        # Выбираем следующий шаг случайным образом в соответствии с эпсилон-жадным алгоритмом
        if random.uniform(0, 1) < epsilon:

            # Учитываем условие, что длина каравана составляет не более 3 кораблей помимо ледокола
            if len(icebreaker_orders) == 0:
                action_type = 0
                order_num = random.randint(0, len(order_list) - 1)
                take_order = order_list[order_num]

            elif (len(icebreaker_orders) == 1) | (len(icebreaker_orders) == 2):
                if len(order_list) == 0:
                    action_type = 1
                    order_num = random.randint(0, len(icebreaker_orders) - 1)
                    take_order = icebreaker_orders[order_num]
                else:
                    action_type = self.__select_random_action_type()
                    if action_type == 0:
                        order_num = random.randint(0, len(order_list) - 1)
                        take_order = order_list[order_num]
                    if action_type == 1:
                        order_num = random.randint(0, len(icebreaker_orders) - 1)
                        take_order = icebreaker_orders[order_num]
            else:
                action_type = 1
                order_num = random.randint(0, len(icebreaker_orders) - 1)
                take_order = icebreaker_orders[order_num]

            return action_type, take_order, order_num

        # Выбираем следующий шаг в соответствии с некоторым "разумным" алгоритмом
        if len(icebreaker_orders) == 0:
            l = np.zeros((len(order_list),))
            for i in range(len(order_list)):
                time_to_go = self.__calculate_best_path(G, icebreaker_position, order_list[i][0], icebreaker_orders,
                                                 ship_type, date, max_G_date)
                l[i] = np.max([date + time_to_go, order_list[i][2]])
            action_type = 0
            num_order_in_list = np.argmin(l)
            order = order_list[num_order_in_list]
            return action_type, order, num_order_in_list

        elif (len(order_list) == 0) | (len(icebreaker_orders) > 2):
            order, num_order_in_list, _, _, _ = self.__best_way_to_make_all_orders(G, icebreaker_position,
                                                                            icebreaker_orders.copy(), ship_type,
                                                                            date,
                                                                            max_G_date)
            action_type = 1
            return action_type, order, num_order_in_list

        else:
            l = np.zeros((len(order_list), 2))

            for i in range(len(order_list)):
                time_to_go = self.__calculate_best_path(
                    G, icebreaker_position, order_list[i][0], icebreaker_orders,
                    ship_type, date, max_G_date
                )
                new_date = np.max([date + time_to_go, order_list[i][2]])
                new_orders = icebreaker_orders.copy()
                new_orders.append(order_list[i])
                _, _, _, _, dr = self.__best_way_to_make_all_orders(G, order_list[i][0], new_orders.copy(), ship_type,
                                                             new_date, max_G_date)
                l[i, 0] = dr

            ox, n_ox, st, new_icebreaker_position, sr = self.__best_way_to_make_all_orders(G, icebreaker_position,
                                                                                    icebreaker_orders.copy(),
                                                                                    ship_type,
                                                                                    date, max_G_date)
            for i in range(len(order_list)):
                l[i, 1] += sr
                time_to_go = self.__calculate_best_path(
                    G, new_icebreaker_position, order_list[i][0], icebreaker_orders, ship_type, st, max_G_date
                )
                new_date = np.max([st + time_to_go, order_list[i][2]])

                wt = self.__calculate_best_path(
                    G, order_list[i][0], order_list[i][1], [order_list[i]], ship_type,
                    new_date, max_G_date
                )
                l[i, 1] += new_date + wt - order_list[i][2]

            idx, action_type = np.unravel_index(np.argmin(l), l.shape)
            if action_type == 0:
                return action_type, order_list[idx], idx
            return action_type, ox, n_ox  # для action_type == 1

    def play_episode(
            self, G, number_of_icebreakers, order_list, epsilon,
            start_icebreaker_position, start_icebreaker_order_list,
            start_date, start_reward, max_G_date, print_results=False
    ):
        icebreaker_orders = start_icebreaker_order_list
        icebreaker_position = start_icebreaker_position

        move = 0
        reward = start_reward
        list_of_actions = list()

        icebreakers_next_move = np.zeros((number_of_icebreakers, 2))
        icebreakers_next_move[:, 0] = np.arange(number_of_icebreakers)
        icebreakers_next_move[:, 1] = start_date
        icebreakers_next_move = pd.DataFrame(icebreakers_next_move)
        icebreakers_next_move.columns = ["icebreaker_number", "next_move_time"]

        while len(order_list) + sum([len(w) for w in icebreaker_orders]) > 0:
            if print_results:
                print_play_episode_start(move, order_list, icebreaker_orders, icebreaker_position)

            # Сортируем по дате, берем ближайший по дате действия ледокол
            icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
            date = icebreakers_next_move.next_move_time.iloc[0]
            icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])
            ship_type = (icebreaker_to_move, 1)

            if (len(order_list) == 0) & (len(icebreaker_orders[icebreaker_to_move]) == 0):
                icebreakers_next_move.next_move_time.iloc[0] = np.inf
                continue

            if print_results:
                print_play_episode_log(date, icebreaker_to_move, icebreakers_next_move)

            # Action - выбор действия в соответствии с эпсилон-жадной стратегией
            # action_type = 0 - берем заявку, action_type = 1 - исполняем заявку
            action_type, take_order, order_num = self.__playout_strategy_player(
                G, epsilon, icebreaker_position[icebreaker_to_move],
                order_list.copy(), icebreaker_orders[icebreaker_to_move].copy(),
                ship_type, date, max_G_date
            )
            list_of_actions.append([action_type, order_num])

            if action_type == 0:
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__take_order_function(G, take_order, order_num,
                                                                                      order_list.copy(),
                                                                                      icebreaker_orders[
                                                                                          icebreaker_to_move].copy(),
                                                                                      icebreaker_position[
                                                                                          icebreaker_to_move],
                                                                                      ship_type, date, max_G_date)
            if action_type == 1:
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__make_order_function(G, take_order, order_num,
                                                                                      order_list.copy(),
                                                                                      icebreaker_orders[
                                                                                          icebreaker_to_move].copy(),
                                                                                      icebreaker_position[
                                                                                          icebreaker_to_move],
                                                                                      ship_type, date, max_G_date)
                # Рассчитываем суммарную награду как разность текущей даты и желаемой даты начала плавания корабля из заявки
                reward += icebreakers_next_move.next_move_time.iloc[0] - take_order[2]

                # Переходим к следующему ходу в игре
            move += 1
            if print_results:
                print_play_episode_end(action_type, take_order, order_num, icebreaker_orders, date, reward)

        return -reward, list_of_actions

    def play_actions(self, actions_list, number_of_icebreakers, G, order_list, start_icebreaker_position,
                     start_icebreaker_order_list, start_date, start_reward, max_G_date, print_results=False):

        icebreaker_orders = start_icebreaker_order_list
        icebreaker_position = start_icebreaker_position
        date = start_date
        reward = start_reward

        icebreakers_next_move = np.zeros((number_of_icebreakers, 2))
        icebreakers_next_move[:, 0] = np.arange(number_of_icebreakers)
        icebreakers_next_move[:, 1] = start_date
        icebreakers_next_move = pd.DataFrame(icebreakers_next_move)
        icebreakers_next_move.columns = ["icebreaker_number", "next_move_time"]
        icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])

        icebreakers_next_move, order_list, icebreaker_orders, reward, move = self.__play_all_actions(
            actions_list, G, order_list, icebreaker_orders, icebreaker_position, icebreakers_next_move,
            date, reward, max_G_date, print_results=print_results
        )

        possible_actions_list = list()
        icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
        icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])

        if len(icebreaker_orders[icebreaker_to_move]) == 0:
            possible_action_type = 0
            for i in range(len(order_list)):
                possible_actions_list.append([possible_action_type, i])

        elif len(icebreaker_orders[icebreaker_to_move]) > 2:
            possible_action_type = 1
            for i in range(len(icebreaker_orders[icebreaker_to_move])):
                possible_actions_list.append([possible_action_type, i])
        else:
            possible_action_type = 0
            for i in range(len(order_list)):
                possible_actions_list.append([possible_action_type, i])
            possible_action_type = 1
            for i in range(len(icebreaker_orders[icebreaker_to_move])):
                possible_actions_list.append([possible_action_type, i])

        icebreakers_next_move = icebreakers_next_move.sort_values(by=["icebreaker_number"])
        dt_date = np.array(icebreakers_next_move.next_move_time)

        return -reward, order_list, icebreaker_orders, icebreaker_position, dt_date, move, possible_actions_list

    def calculate_result_plan(self, actions_list, number_of_icebreakers, G, order_list, start_icebreaker_position,
                       start_icebreaker_order_list, start_date, start_reward, max_G_date):
        icebreaker_orders = start_icebreaker_order_list
        icebreaker_position = start_icebreaker_position
        move = 0
        reward = start_reward

        result_list = list()

        icebreakers_next_move = np.zeros((number_of_icebreakers, 2))
        icebreakers_next_move[:, 0] = np.arange(number_of_icebreakers)
        icebreakers_next_move[:, 1] = start_date
        icebreakers_next_move = pd.DataFrame(icebreakers_next_move)
        icebreakers_next_move.columns = ["icebreaker_number", "next_move_time"]
        icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])

        for i in range(len(actions_list)):
            # Сортируем по дате, берем ближайший по дате действия ледокол
            icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
            date = icebreakers_next_move.next_move_time.iloc[0]
            icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])
            ship_type = (icebreaker_to_move, 1)

            while len(order_list) + len(icebreaker_orders[icebreaker_to_move]) <= 0:
                icebreakers_next_move.next_move_time.iloc[0] = np.inf
                icebreakers_next_move = icebreakers_next_move.sort_values(by=['next_move_time', "icebreaker_number"])
                date = icebreakers_next_move.next_move_time.iloc[0]
                icebreaker_to_move = int(icebreakers_next_move.icebreaker_number.iloc[0])
                ship_type = (icebreaker_to_move, 1)

            action_type, order_num = actions_list[i]

            result_list.append(
                [icebreaker_to_move, action_type, icebreaker_orders[icebreaker_to_move],
                 icebreaker_position[icebreaker_to_move],
                 0, icebreakers_next_move.next_move_time.iloc[0], 0])

            if action_type == 0:
                take_order = order_list[order_num]
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__take_order_function(G, take_order, order_num,
                                                                                      order_list.copy(),
                                                                                      icebreaker_orders[
                                                                                          icebreaker_to_move].copy(),
                                                                                      icebreaker_position[
                                                                                          icebreaker_to_move],
                                                                                      ship_type, date, max_G_date)

            if action_type == 1:
                take_order = icebreaker_orders[icebreaker_to_move][order_num]
                order_list, icebreaker_orders[icebreaker_to_move], icebreaker_position[icebreaker_to_move], \
                    icebreakers_next_move.next_move_time.iloc[0] = self.__make_order_function(G, take_order, order_num,
                                                                                      order_list.copy(),
                                                                                      icebreaker_orders[
                                                                                          icebreaker_to_move].copy(),
                                                                                      icebreaker_position[
                                                                                          icebreaker_to_move],
                                                                                      ship_type, date, max_G_date)
                reward += icebreakers_next_move.next_move_time.iloc[0] - take_order[2]

            result_list[-1][4] = icebreaker_position[icebreaker_to_move]
            result_list[-1][6] = icebreakers_next_move.next_move_time.iloc[0]

            # Переходим к следующему ходу в игре
            move += 1

        return result_list
