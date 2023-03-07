"""
Read item history from zabbix, and plot as histogram
"""
import numpy
from pyzabbix import ZabbixAPI
import sys
import logging
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
# import requests
# import json
import time
import datetime
import urllib3

url = 'http://192.168.1.200:8080'
login = 'Admin'
password = 'zabbix'
HOURS = 10 * 1

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# stream = logging.StreamHandler(sys.stdout)
# stream.setLevel(logging.DEBUG)
# log = logging.getLogger('pyzabbix')
# log.addHandler(stream)
# log.setLevel(logging.DEBUG)
zapi = ZabbixAPI(url=url, user='Admin', password='zabbix')
# zapi.session.verify = False
# zapi.timeout = 5.1
# zapi.login(login, password)


item = zapi.item.get(itemids=42269)[0]
triggers = zapi.trigger.get(itemids=item['itemid'])[0]

begin = int(time.mktime(datetime.datetime.now().timetuple()) - 3600 * 3)

history_data = zapi.history.get(output='extend', itemids=item['itemid'], history=0,
                                sortfield='clock', time_from=begin)

def timestamp_control(timeStamp, para):
    timeArray = time.localtime(int(timeStamp))
    date_time = time.strftime(para, timeArray)
    return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")


x_values = []
y_values = []


for data_stamp in history_data:
  clock = timestamp_control(data_stamp['clock'], "%Y-%m-%d %H:%M:%S")
  value = float('{:.4f}'.format(float(data_stamp["value"])))
  #value = int('{:.0%}'.format(float(data_stamp["value"]))[:-1])
  x_values.append(clock)
  y_values.append(value)


fig, ax = plt.subplots()
# plt.style.use('dark_background')
px = 1/plt.rcParams['figure.dpi']
fig = plt.figure(figsize=(1016*px, 354*px), dpi=80)
# fig.set_size_inches()
ax = plt.subplot(111)

# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
for i, label in enumerate(ax.get_xticklabels(which='major')):
    x = len(ax.get_xticklabels(which='major'))
    if not i == x - 1:
        pass
        label.set(rotation=0, horizontalalignment='center')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    else:
        label.set(rotation=15, horizontalalignment='center')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        xformatter = mdates.DateFormatter('%H:%M')
        xlocator = mdates.MinuteLocator(byminute=[0, 15, 30, 45], interval=1)
        ax.xaxis.set_major_locator(xlocator)
        plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)






    # label.set(rotation=30, horizontalalignment='right')


if item['units'] == '%':
    plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter(decimals=1))
else:
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%f {}'.format(item['units'])))
# plt.ylabel(item['units'][1:], fontsize=10, rotation="vertical")
plt.title(item['name'])
AVG = np.mean(y_values)
# ax.axhspan(AVG-0.1, AVG+0.5, facecolor='#e9e9c6', alpha=0.5)
# ax.annotate(f"Average-{AVG:.4f} bar", xy=(1.01, AVG / (max(y_values) + 10) - .01), xycoords='axes fraction', color='red',fontsize=10)
# parse the sizes for the first, middle, and last entries
# args = ('11111', '22222')



# data = [{'': item['name'], "AVG": '{:.4f} {}'.format(numpy.average(y_values), item['units'])},
#         {'': 'trigger', "AVG": 0}]
# dff = pd.DataFrame(data)
# table = ax.table(cellText=dff.values, colLabels=dff.columns, loc='upper center', cellLoc='center',
#                  bbox=[0, -0.7, 1, 0.3])
# table.auto_set_column_width(col=list(range(len(dff.columns))))
# table.auto_set_column_width(col=list(range(len(dff.columns))))


d = {'mean':'AverageDays','min':'LowestNumberOfDays','max':'HighestNumberOfDays'}
# df = (pd.DataFrame.groupby(['Class', 'Code', 'Vendor', 'State'])['NumberOfDays']
#         .agg(['mean','min','max'])
#         .rename(columns=d)
#         .reset_index())

ax.pivot_table(index=['Class','Code','Vendor','State'],
               values='NumberOfDays',
               aggfunc=('min','mean','max')).rename(columns=d).reset_index()



fig.figure.subplots_adjust(bottom=0.4)

# the_table = ax.table(cellText=table_vals, rowLoc='right', rowColours='red',
#                      rowLabels=row_labels, colWidths=[.5,.5], colLabels=col_labels,
#                      colLoc='center', loc='bottom', bbox=[0, -0.3, 1, 0.275])
# ax.tight_layout(rect=[0.11, 0.3, 0.95, .95])
# plt.text(12,3.4,'Table Title',size=8)
data_line = ax.plot(x_values, y_values,)
# mean_line = ax.plot(x_values, [np.mean(y_values)]*len(y_values), label='triggers', linestyle='--')
plt.axhline(y=0.9, color='r', linestyle='--')
# show that the estimated min and max sizes are 1.6 and 98.4, respectively
# plt.legend(*args, **{'title': "I want the true min-med-max here! [thanks for taking a look:)]", 'bbox_to_anchor': (1, 1)}, loc='upper center', bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=2,frameon=False)
# Make a legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=2, frameon=False)
plt.grid(color='gray', linestyle='dashed', linewidth=0.7)
plt.show()


exit(0)
newrows = np.array(xxx)

fig = plt.figure(1, (16, 6))
ax = plt.gca()
# ax.grid(alfa=0.2)

ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f %%"))

# import matplotlib.dates as dates
# new_x = dates.num2date(x_values)
# ax.plot_date(x_values, y_values, linestyle='-', marker='', linewidth=1)

# ax.fill_between(x=x_values, y1=min(y_values), y2=y_values, where=max(y_values) >= min(y_values), alpha=0.2)
# ax.set_xlim(np.datetime64(x_values[0], 'D'), np.datetime64(x_values[-1], 'D') + np.timedelta64(1, 'D'), auto=False)

ax.xaxis.set_major_formatter(mdate.DateFormatter('%m-%d %H:%M'))

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# plt.gcf().autofmt_xdate()
# plt.plot(x_values, y_values, linewidth=1)

plt.title("{0}\nMaxinum: , Mininum: , Average: , Peak_Time: ".format(picture_title), fontsize=20)
# plt.xlabel(label, fontsize=20, rotation="horizontal")
# plt.ylabel(label, fontsize=10, rotation="horizontal")
plt.tick_params(axis='both', labelsize=20)
plt.show()






xxx = 7

xxx = 4
pass

exit(0)
print('Begin loop for history...')
for item in items:
    ret = zapi.history.get(itemids=item['itemid'], time_from=begin, history=item['value_type'])
    xxx = []
    for x in ret:
        xxx.append((x['clock'], float(x['value'])))

    newrows = np.array(xxx)
    history = map(lambda x: float(x['value']), ret)
    x = newrows[:, 1]
    y = newrows[:, 2]
    plt.title('item: ' + item['itemid'])
    plt.xlabel('time')
    plt.ylabel('value')
    plt.plot(x, y)
    plt.show()

    plt.figure()
    plt.hist(v, bins=200, normed=1)
    plt.title('item: ' + item['itemid'])

    #  lline = numpy.percentile(v, 25)
    #  uline = numpy.percentile(v, 75)
    #  length = uline - lline
    #  low = lline - length
    #  up = uline + length
    #  print(low, up)
    plt.figure()
    plt.boxplot(v, sym='+', notch=True)
    plt.title('item: ' + item['itemid'])
    plt.show()
