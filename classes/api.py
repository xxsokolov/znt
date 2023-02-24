from __future__ import annotations
from typing import Any

import uvicorn
from fastapi import FastAPI, Depends, Query, status
from classes.logger import Log
from pydantic import BaseModel, Field


class SendMessage(BaseModel):
    title: str = Field(description="Укажите @username или Chat Name", include_in_schema=True)
    period: str = Field(description="The description of the item")
    header: str = Field(description="The description of the item")
    body: str = Field(description="The description of the item")
    hostname: str = Field(default='Zabbix server', description="The description of the item")
    itemid: str = Field(default='23271 *UNKNOWN* *UNKNOWN* *UNKNOWN*', description="The description of the item")
    hostid: str = Field(default='10084', description="The description of the item")
    triggerid: str = Field(default='13486', description="The description of the item")
    triggerurl: str = Field(default='Zabbix server', description="The description of the item")
    eventtags: str = Field(default='target:zabbix, ZNTMentions:@xxsokolov', description="The description of the item")
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


api = FastAPI(debug=True)
v1 = FastAPI(debug=True)
api.mount("/api/v1", v1)

logger = Log(True).log


def run(host="0.0.0.0", port=8000):
    return uvicorn.run(api, host=host, port=port)


@v1.post("/telegram/sendMessage", status_code=status.HTTP_202_ACCEPTED)
def send_message(chat_id: str, send_message: SendMessage):
    results = dict(state='Ok', data=send_message)
    return results


@v1.get("/telegram/sendMessage", status_code=status.HTTP_200_OK)
def get_example():
    return SendMessage.construct()
