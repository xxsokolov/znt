from __future__ import annotations
import uvicorn
from fastapi import FastAPI, status
from classes.logger import Log
from pydantic import BaseModel, Field


class send(BaseModel):
    title: str = Field(title='Chat ID', description="Укажите @username или Chat Name", include_in_schema=True)
    period: str = Field(title='Text', description="The description of the item")
    header: str = Field(title='Text', description="The description of the item")
    body: str = Field(title='Text', description="The description of the item")

class macros(BaseModel):
    hostname: str = Field(default='Zabbix server', title='Text', description="The description of the item")
    itemid: str = Field(default='23271 *UNKNOWN* *UNKNOWN* *UNKNOWN*', title='Text', description="The description of the item")
    hostid: str = Field(default='10084', title='Text', description="The description of the item")
    triggerid: str = Field(default='13486', title='Text', description="The description of the item")
    triggerurl: str = Field(default='Zabbix server', title='Text', description="The description of the item")
    eventtags: str = Field(default='target:zabbix, ZNTMentions:@xxsokolov', title='Text', description="The description of the item")
    eventid: str = Field(default='55', title='Text', description="The description of the item")
    actionid: str = Field(default='7', title='Text', description="The description of the item")

class znt(BaseModel):
    graphs: bool = True
    hostlinks: bool = True
    graphlinks: bool = True
    acklinks: bool = True
    eventlinks: bool = True
    triggerlinks: bool = True
    eventtag: bool = True
    eventidtag: bool = True
    itemidtag: bool = True
    triggeridtag: bool = True
    actionidtag: bool = True
    hostidtag: bool = True
    zntsettingstag: bool = True
    zntmentions: bool = True
    keyboard: bool = True
    graphs_period: str = 'default'


api = FastAPI(debug=True)
v1 = FastAPI(debug=True)
api.mount("/api/v1", v1)

logger = Log(True).log


def run(host="0.0.0.0", port=80):
    return uvicorn.run(api, host=host, port=port)


@v1.post("/telegram/sendMessage", status_code=status.HTTP_202_ACCEPTED)
def read_item(
        chat_id: str,
        send: send,
        macro: macros,
        znt: znt
):
    results = {"state": 'Ok'}
    return results

# znt = FastAPI()
# v1 = FastAPI()
#
# # @znt.on_event('startup')
# # def startup():
# #     logger = Log(True).log
# #     bot_config = ReadYaml(logger=logger, path='../.bots.yaml').read_bots_yaml()
#
# @v1.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     xxx = 2
#     return {"item_id": item_id, "q": q}
#
# znt.mount("/api/v1", v1)
# if __name__ == "__main__":
#     uvicorn.run("__main__:znt", host="0.0.0.0", port=8000, reload=True, workers=1)
# # uvicorn main:app --reload
