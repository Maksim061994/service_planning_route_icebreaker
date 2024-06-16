from loguru import logger


def print_results_start(
        actions_list, order_list, icebreaker_orders, icebreaker_position, date, reward
):
    logger.info(f'{actions_list=}')
    logger.info(f'{order_list=}', )
    logger.info(f'{icebreaker_orders=}', )
    logger.info(f'{icebreaker_position=}', )
    logger.info(f'{date=}', )
    logger.info(f'{reward=}')
    logger.info(30 * '---')


def print_results_end(
        icebreakers_next_move, icebreaker_to_move, date, action_type, take_order, order_num,
        order_list, icebreaker_orders, icebreaker_position, reward
):
    logger.info(f'{icebreakers_next_move=}')
    logger.info(f'{icebreaker_to_move=}')
    logger.info(f'{action_type=}')
    logger.info(f'{take_order=}, {order_num=}')
    logger.info(f'{order_list=}', )
    logger.info(f'{icebreaker_orders=}', )
    logger.info(f'{icebreaker_position=}', )
    logger.info(f'{date=}', )
    logger.info(f'{reward=}')
    logger.info(30 * '---')


def print_play_episode_start(move, order_list, icebreaker_orders, icebreaker_position):
    logger.info(f'{move=}')
    logger.info(f'{order_list=}')
    logger.info(f'{icebreaker_orders=}')
    logger.info(f'{icebreaker_position=}')


def print_play_episode_log(date, icebreaker_to_move, icebreakers_next_move):
    logger.info(f'{date=}')
    logger.info(f'{icebreaker_to_move=}')
    logger.info(f'{icebreakers_next_move=}')


def print_play_episode_end(action_type, take_order, order_num, icebreaker_orders, date, reward):
    logger.info(f'{action_type=}')
    logger.info(f'{take_order=}, {order_num=}')
    logger.info(f'{icebreaker_orders=}')
    logger.info(f'{date=}')
    logger.info(f'{reward=}')
    logger.info(30 * '---')
