import pandas as pd

def find_sheet_name(excel, date):
    '''
        Лист с актуальными данными по тяжести льда
    '''
    date = pd.to_datetime(date,dayfirst=True)
    date_return = []
    for date_ in excel.sheet_names[2:]:
        if pd.to_datetime(date_,dayfirst=True) <= date:
            date_return = date_
            continue
        else:
            return date_return
    return date_

def calc_speed_Arc0_3(speed, icebreaker=False):
    '''
        Расчет скоростей для классов 0-3
    '''
    if icebreaker:
        speed_0 = speed
        speed_1 = speed
        speed_2 = -10
    else:
        speed_0 = speed
        speed_1 = -10
        speed_2 = -10
    return speed_0, speed_1, speed_2

def calc_speed_Arc4_6(speed, icebreaker=False):
    '''
        Расчет скоростей для классов 4-6
    '''
    if icebreaker:
        speed_0 = speed
        speed_1 = 0.8 * speed
        speed_2 = 0.7 * speed
    else:
        speed_0 = speed
        speed_1 = -10
        speed_2 = -10
    
    return speed_0, speed_1, speed_2

def calc_speed_Arc7(speed, icebreaker=False):
    '''
        Расчет скоростей для класса 7
    '''
    if icebreaker:
        speed_0 = speed
        speed_1 = 0.6 * speed
        speed_2 = 0.15 * speed
    else:
        speed_0 = speed
        speed_1 = 0.6 * speed
        speed_2 = -10
    return speed_0, speed_1, speed_2

def find_ship_speed_map(df, name_ship, class_ship, speed_ship, icebreaker):
    '''
        Расчет карты скоростей в зависимости от класса и скорости судна
    '''
    const = 1.852
    ship_class3 = ['Нет','Arc 1','Arc 2','Arc 3']
    ship_class4_6 = ['Arc 4','Arc 5','Arc 6']
    ship_class7 = ['Arc 7']
    ship_class9 = ['Arc 9']
    
    df_ship = df.copy()
    df_ship = df_ship.round()    
    df_ship[df_ship < 10] = -10.0
    # Ледокол
    if class_ship in ship_class9:
        if name_ship in ['50 лет Победы','Ямал']:
            df_ship[df_ship > speed_ship] = speed_ship
            df_ship[df_ship > 0] = df_ship[df_ship > 0].apply(lambda x: round((x*const)/25, 3))
        else:
            df_ship[(df_ship >= 10)&(df_ship <= 14)] = df_ship[(df_ship >= 10)&(df_ship <= 14)]*0.75
            df_ship[(df_ship >= 15)&(df_ship <= 19)] = df_ship[(df_ship >= 15)&(df_ship <= 19)]*0.9
            df_ship[df_ship > 19] = speed_ship
            df_ship[df_ship > 0] = df_ship[df_ship > 0].apply(lambda x: round((x*const)/25, 3))
        return df_ship
    else:        
        df_ship[(df_ship >= 10)&(df_ship <= 14)] = 2
        df_ship[(df_ship >= 15)&(df_ship <= 19)] = 1
        df_ship[df_ship > 19] = 0
        
        if class_ship in ship_class3:
            if icebreaker:
                speed_0, speed_1, speed_2 = calc_speed_Arc0_3(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), round((speed_1*const)/25, 3), speed_2
            else:
                speed_0, speed_1, speed_2 = calc_speed_Arc0_3(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), speed_1, speed_2
            
        if class_ship in ship_class4_6:
            if icebreaker:
                speed_0, speed_1, speed_2 = calc_speed_Arc4_6(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), round((speed_1*const)/25, 3), round((speed_2*const)/25, 3)
            else:
                speed_0, speed_1, speed_2 = calc_speed_Arc4_6(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), speed_1, speed_2
            
        if class_ship in ship_class7:
            if icebreaker:
                speed_0, speed_1, speed_2 = calc_speed_Arc7(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), round((speed_1*const)/25, 3), round((speed_2*const)/25, 3)
            else:
                speed_0, speed_1, speed_2 = calc_speed_Arc7(speed_ship,icebreaker)
                time_0, time_1, time_2 = round((speed_0*const)/25, 3), round((speed_1*const)/25, 3), speed_2
            
    time_arch = df_ship.replace({0:time_0, 1:time_1, 2:time_2})

    return time_arch

def compute_speed_by_date_for_ship(
    dataframe: pd.ExcelFile, 
    date: str,
    name_ship: str,
    class_ship: str,
    speed_ship: float,
    icebreaker: bool = False
) -> pd.DataFrame:
    """ 
    На выходе датафрейм с временами прохождения ячеек
    """
    date_excel = find_sheet_name(dataframe, date=date)    
    df = dataframe.parse(date_excel, header=None)
    speed_map = find_ship_speed_map(df, name_ship, class_ship, speed_ship, icebreaker)
    return speed_map