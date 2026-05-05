
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
# from uuid import UUID
from enum import Enum


class ProjectState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ARCHIVED = "Archived"


class UserInfo(BaseModel):
    date_added: datetime
    user_id: int
    who_added: int


class ProjectCreate(BaseModel):
    web_users: List[int] = Field(default_factory=list)
    prj_loc_city: Optional[str] = None
    web_users_info: List[UserInfo] = Field(default_factory=list)
    created_on: datetime
    prj_desc: Optional[str] = None
    prj_loc_country: Optional[str] = None
    mobile_users_info: List[UserInfo] = Field(default_factory=list)
    customer_id: int
    prj_name: str
    prj_date: Optional[str] = None  
    prj_id: str
    created_by: int
    prj_addr: Optional[str] = None
    prj_loc_state: Optional[str] = None
    prj_state: ProjectState

class ProjectUpdate(BaseModel):
    web_users: Optional[List[int]] = None
    prj_loc_city: Optional[str] = None
    web_users_info: Optional[List[UserInfo]] = None
    created_on: Optional[datetime] = None
    prj_desc: Optional[str] = None
    prj_loc_country: Optional[str] = None
    mobile_users_info: Optional[List[UserInfo]] = None
    customer_id: Optional[int] = None
    prj_name: Optional[str] = None
    prj_date: Optional[str] = None
    created_by: Optional[int] = None
    prj_addr: Optional[str] = None
    prj_loc_state: Optional[str] = None
    prj_state: Optional[ProjectState] = None







# b.	Payload:
# {
#   "web_users": [
#     265
#   ],
#   "prj_loc_city": "Dubai",
#   "web_users_info": [
#     {
#       "date_added": "2016-09-18T16:22:36.132Z"(date format),
#       "user_id": 265,
#       "who_added": 266
#     }
#   ],
#   "created_on": "2016-09-18T16:22:36.092Z",
#   "prj_desc": "Clinical",
#   "prj_loc_country": "United Arab Emirates",
#   "mobile_users_info": [
#     {
#       "date_added": "2016-09-18T16:33:06.875Z",
#       "user_id": 266,
#       "who_added": 265
#     },
#     {
#       "date_added": "2016-09-18T18:48:22.702Z",
#       "user_id": 267,
#       "who_added": 265
#     }
#   ],
#   "customer_id": 28,
#   "prj_name": "Homecare Dept Tracking",
#   "prj_date": "20 October 2022"(todays date),
#   "prj_id": "026fd614-7d8e-11e6-bafd-f23c91e268d3"(uuid),
#   "created_by": 265,
#   "prj_addr": "Liwa Building, 4th Floor Khalej Arabic St # 30",
#   "prj_loc_state": "Dubai",
#   "prj_state": "Active"
# }
