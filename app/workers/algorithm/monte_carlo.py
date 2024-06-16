from loguru import logger
import random
import numpy as np
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')

from app.workers.algorithm.tree import Tree


class MonteCarlo:

    def __init__(
            self,
            player, number_step: int,
            G: dict, C: float = 0.5, D: int = 10000, T: int = 10, W: float = 0.8,
            eps: float = 0.03,
    ):
        self.number_step = number_step
        self.G = G
        self.C = C
        self.D = D
        self.T = T
        self.W = W
        self.eps = eps
        self.player = player

    def __selection_strategy(self, node):
        """
        Selection strategy
        :param node: Tree
        :return:
        """
        is_selected = False
        while len(node.childs) > 0:
            # Если дошли до конечной ноды, заканчиваем поиск
            if node.end_node == True:
                break

                # Если у ноды есть ребенок, у которых не было ни одного посещения, выбираем его
            for i in range(len(node.childs)):
                if node.childs[i].number_of_visits == 0:
                    node = node.childs[i]
                    is_selected = True
                    break

            if is_selected == True:
                break

            # Если у всех детей были посещения, движемся дальше
            # Если общее количество ноды меньше константы Т, осуществяем выбор ребенка случайным образом
            if node.number_of_visits <= self.T:
                if len(node.childs) > 0:
                    node = random.choice(node.childs)

            # Иначе выбираем ребенка по методу UCB
            else:
                ucb_array = np.zeros((len(node.childs),))
                for i in range(len(node.childs)):
                    v = node.childs[i].mean_value + self.W * node.childs[i].max_value
                    s1 = np.log(node.number_of_visits) / node.childs[i].number_of_visits
                    s2 = (node.childs[i].sum_squared_results + node.childs[i].number_of_visits * v ** 2 + self.D) / \
                         node.childs[i].number_of_visits
                    ucb_array[i] = v - self.C * s1 ** 0.5 - s2 ** 0.5
                selected_node = np.argmax(ucb_array)
                node = node.childs[selected_node]
        return node

    def __play_out_strategy(
            self, node, number_of_icebreakers, order_list,
            start_icebreaker_position, start_icebreaker_order_list, start_date, start_reward, max_G_date,
            verbose=False
    ):
        """
        Play-Out strategy
        :param node:
        :return:
        """
        # Находим путь до узла по предыдущим действиям начиная со стартового положения
        a_node = node
        actions_list = list()
        for i in range(self.number_step):
            if not a_node.parent:
                break
            else:
                actions_list.append(a_node.action)
                a_node = a_node.parent

        actions_list = actions_list[::-1]
        played_reward, played_order_list, played_icebreaker_orders, \
         played_icebreaker_position, played_date, played_move, _ = self.player.play_actions(
            actions_list=actions_list.copy(),
            number_of_icebreakers=number_of_icebreakers,
            G=self.G,
            order_list=order_list.copy(),
            start_icebreaker_position=start_icebreaker_position.copy(),
            start_icebreaker_order_list=start_icebreaker_order_list.copy(),
            start_date=start_date.copy(),
            start_reward=start_reward,
            max_G_date=max_G_date
        )

        new_reward, new_list_of_actions = self.player.play_episode(
            G=self.G, epsilon=self.eps, number_of_icebreakers=number_of_icebreakers, order_list=played_order_list.copy(),
            start_icebreaker_position=played_icebreaker_position.copy(),
            start_icebreaker_order_list=played_icebreaker_orders.copy(),
            start_date=played_date.copy(), start_reward=-played_reward, max_G_date=max_G_date,
            print_results=verbose
        )
        return actions_list, played_move, new_reward, new_list_of_actions

    def mcts(
            self,
            number_of_icebreakers, order_list, start_icebreaker_position,
            start_icebreaker_order_list, start_date, start_reward, max_G_date,
            verbose=False
    ):
        root_node = Tree('root')

        for node_to_expanse in tqdm(range(self.number_step)):
            node = root_node

            # Selection strategy
            node = self.__selection_strategy(node)
            if node.end_node == True:
                break

            # Play-Out strategy
            actions_list, played_move, new_reward, new_list_of_actions = self.__play_out_strategy(
                node=node, number_of_icebreakers=number_of_icebreakers, order_list=order_list,
                start_icebreaker_position=start_icebreaker_position,
                start_icebreaker_order_list=start_icebreaker_order_list,
                start_date=start_date, start_reward=start_reward, max_G_date=max_G_date,
                verbose=verbose
            )

            # Expansion strategy
            a_node = node
            a_list = actions_list.copy()
            for i in range(len(new_list_of_actions)):
                if len(a_node.childs) == 0:
                    _, _, _, _, _, _, possible_actions_list = self.player.play_actions(
                        actions_list=a_list.copy(),
                        number_of_icebreakers=number_of_icebreakers,
                        G=self.G,
                        order_list=order_list.copy(),
                        start_icebreaker_position=start_icebreaker_position.copy(),
                        start_icebreaker_order_list=start_icebreaker_order_list.copy(),
                        start_date=start_date.copy(),
                        start_reward=start_reward,
                        max_G_date=max_G_date)

                    for j in range(len(possible_actions_list)):
                        child = Tree(f'child_{a_node.name}_{j}')
                        child.parent = a_node
                        child.action = possible_actions_list[j]

                        # Вписываем полученный результат симуляции в созданную child-node с соответствующим действием (т.е. первое действие симуляции)
                        if possible_actions_list[j] == new_list_of_actions[0]:
                            child.mean_value = new_reward
                            child.max_value = new_reward
                            child.sum_squared_results = new_reward ** 2
                            child.number_of_visits = 1.0

                        a_node.append_node(child)
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
                        logger.warning(vars(a_node))
                        logger.warning(new_list_of_actions[i], child_actions)
                        logger.warning("ERROR: NO CHILD WITH SAME ACTION!")

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
            if verbose:
                if node_to_expanse % 100 == 0:
                    logger.info("step:", node_to_expanse, "best_reward:", root_node.max_value)
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
