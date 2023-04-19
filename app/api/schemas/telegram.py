# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from pydantic import BaseModel, Field


class Message(BaseModel):
    send_to: str = Field(default=None, description="Укажите @username или Chat Name")
    bot: str = Field(default='default', description="Укажите @username или Chat Name")
    bot_group: str = Field(default='default', description="Укажите @username или Chat Name")
    title: str = Field(
        default='Zabbix server - Zabbix server: More than 100 items having missing data for more than 10 minutes',
        description="Укажите @username или Chat Name")
    period: int = Field(default=10800, description="The description of the item")
    header: str = Field(
        default='{Problem} Warning {Warning}: Zabbix server: More than 100C:: items having missing data for more than 10 minutes',
        description="The description of the item")
    body: str = Field(
        default='Host: Zabbix server [127.0.0.1]\nLast value: 0 (12:40:52)\nDuration: 1s\nhost: Zabbix server',
        description="The description of the item")
    hostname: str = Field(default='Zabbix server', description="The description of the item")
    itemid: str = Field(default='23271 *UNKNOWN* *UNKNOWN* *UNKNOWN*', description="The description of the item")
    hostid: str = Field(default='10084', description="The description of the item")
    triggerid: str = Field(default='13486', description="The description of the item")
    triggerurl: str = Field(default='Zabbix server', description="The description of the item")
    eventtags: str = Field(default='', description="target:zabbix, ZNTMentions:@xxsokolov, ZNTMentions:@xxsokolov, znts:dash=YGLp1d14k, znts:bot=@username")
    eventid: str = Field(default='55', description="The description of the item")
    actionid: str = Field(default='7', description="The description of the item")
    graphs: bool = Field(default=True, description="The description of the item")
    hostlinks: bool = Field(default=True, description="The description of the item")
    graphlinks: bool = Field(default=True, description="The description of the item")
    acklinks: bool = Field(default=True, description="The description of the item")
    eventlinks: bool = Field(default=True, description="The description of the item")
    triggerlinks: bool = Field(default=True, description="The description of the item")
    eventtag: bool = Field(default=True, description="The description of the item")
    eventidtag: bool = Field(default=True, description="The description of the item")
    itemidtag: bool = Field(default=True, description="The description of the item")
    triggeridtag: bool = Field(default=True, description="The description of the item")
    actionidtag: bool = Field(default=True, description="The description of the item")
    hostidtag: bool = Field(default=True, description="The description of the item")
    zntsettingstag: bool = Field(default=True, description="The description of the item")
    zntmentions: bool = Field(default=True, description="The description of the item")
    keyboard: bool = Field(default=True, description="The description of the item")
    graphs_period: str = Field(default='default', description="The description of the item")
