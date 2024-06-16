import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pickle

with open('complete_ships.p', 'rb') as fp:
    data = pickle.load(fp)

with open('complete_icebreakers.p', 'rb') as fp:
    data_icebreaker = pickle.load(fp)
# Первый заказ
first_ship = data[0]
x_data = []
y_data = []
status_data = []
for data_ship in first_ship['route']:
    row_, columns_ = data_ship['coords']
    x_data.append(row_)
    y_data.append(columns_)
    status_data.append(data_ship['status'])
# Поиск имени ледокола
for j in first_ship['route']:
    if j['assigned_icebracker'] == None:
        continue
    else:
        name_icebreaker = j['assigned_icebracker']
        for icbreaker_data in data_icebreaker:
            if icbreaker_data['name_icebracker'] == name_icebreaker:
                first_icebreaker = icbreaker_data
                break
        break

x_data_icebreaker = []
y_data_icebreaker = []
status_data_icebreaker = []
order_check = None
order_count = 0
for ii in range(len(first_ship['route'])):
    if order_count < 2:
        dd = first_icebreaker['route'][ii]
        row_r, column_c = dd['grid_coords']
        x_data_icebreaker.append(row_r)
        y_data_icebreaker.append(column_c)
        status_data_icebreaker.append(dd['status'])
        if dd['assigned_ships'] != order_check:
            order_check = dd['assigned_ships']
            order_count += 1
# Загрузка карты льдов
path_excel = 'IntegrVelocity.xlsx'
xls = pd.ExcelFile(path_excel)
Velocity_day = pd.read_excel(path_excel, sheet_name=xls.sheet_names[2], header=None)
color_df = Velocity_day.copy()

# Цветовая гамма тяжести льда
color_df[Velocity_day < 0] = 'gray'
color_df[(Velocity_day >= 0) & (Velocity_day <= 10)] = 'beige'
color_df[(Velocity_day > 10) & (Velocity_day <= 15)] = 'royalblue'
color_df[(Velocity_day > 15) & (Velocity_day <= 19)] = 'mediumblue'
color_df[Velocity_day > 19] = 'darkblue'
# Карта льдов
fig, ax = plt.subplots(figsize=(16,8))
for i in range(color_df.shape[0]):
    for j in range(color_df.shape[1]):
        color_ = color_df.iloc[i,j]
        map_plot = ax.plot(i, j, markersize=4,  color=color_, marker ='s', linestyle='None',zorder=1)
# Маршрут
for i in range(len(x_data)):
    if status_data[i] == 0:
        ship_plot = ax.plot(x_data[i], y_data[i], markersize=3, color='yellow', marker='x', linestyle='None', zorder=4)
    if status_data[i] == 1:
        ship_plot = ax.plot(x_data[i], y_data[i], markersize=1, color='lime', marker='x', linestyle='None', zorder=3)
    if i < len(x_data_icebreaker):
        if status_data_icebreaker[i] == 0:
            icebreaker_plot = ax.plot(x_data_icebreaker[i], y_data_icebreaker[i], markersize=3, color='yellow', marker='o',
                    linestyle='None', zorder=4)
        if status_data_icebreaker[i] == 1:
            icebreaker_plot = ax.plot(x_data_icebreaker[i], y_data_icebreaker[i], markersize=1, color='orange', marker='o',
                    linestyle='None', zorder=3)
        if status_data_icebreaker[i] == 2:
            icebreaker_plot = ax.plot(x_data_icebreaker[i], y_data_icebreaker[i], markersize=1, color='red', marker='o', linestyle='None',
                    zorder=4)
gray_patch = mpatches.Patch(color='gray', label='Тяжесть льда < 0')
beige_patch = mpatches.Patch(color='beige', label='0 <= Тяжесть льда < 10')
royalblue_patch = mpatches.Patch(color='royalblue', label='10 <= Тяжесть льда < 15')
mediumblue_patch = mpatches.Patch(color='mediumblue', label='15 <= Тяжесть льда < 19')
darkblue_patch = mpatches.Patch(color='darkblue', label='Тяжесть льда >= 19')
leg1 = ax.legend(handles=[gray_patch,darkblue_patch, mediumblue_patch,beige_patch,royalblue_patch],loc='upper left', prop={'size': 10})
ax.add_artist(leg1)
yellow_patch = mpatches.Patch(color='yellow', hatch='x', label='Начальная точка корабля/ледокола')
lime_patch = mpatches.Patch(color='lime', hatch='x', label='Корабль движется самостоятельно')
orange_patch = mpatches.Patch(color='orange', hatch='o', label='Ледокол движется к кораблю')
red_patch = mpatches.Patch(color='red', hatch='o', label='Ледокол движется с кораблем')
plt.legend(handles=[yellow_patch,lime_patch,orange_patch,red_patch],loc='upper right', prop={'size': 10})
plt.title(f"Маршурт для первой заявки, корабль - {first_ship['name_ship']}, ледокол - {name_icebreaker}", fontsize=20)
plt.show()