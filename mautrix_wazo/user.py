from __future__ import annotations

import contextlib
from typing import AsyncIterable, Awaitable, TYPE_CHECKING, cast

from mautrix import bridge as br
from mautrix.bridge import BaseUser, BasePortal, BasePuppet
from mautrix.types import UserID, RoomID
from mautrix.util.bridge_state import BridgeState

from .db.user import User as DBUser
from .puppet import Puppet
from .types import WazoUUID

if TYPE_CHECKING:
    from .__main__ import WazoBridge


class UserError(Exception):
    pass


class User(DBUser, BaseUser):
    by_mxid: dict[UserID, User] = {}
    by_uuid: dict[WazoUUID, User] = {}

    @classmethod
    def init_cls(cls, bridge: "WazoBridge") -> None:
        cls.bridge = bridge
        cls.config = bridge.config
        cls.az = bridge.az
        cls.loop = bridge.loop

    async def is_logged_in(self) -> bool:
        pass

    async def get_puppet(self) -> BasePuppet | None:
        pass

    async def get_portal_with(self, puppet: br.BasePuppet, create: bool = True) -> BasePortal | None:
        pass

    async def get_direct_chats(self) -> dict[UserID, list[RoomID]]:
        pass

    async def get_bridge_states(self) -> list[BridgeState]:
        pass

    def _add_to_cache(self):
        self.by_mxid[self.mxid] = self
        self.by_uuid[self.wazo_uuid] = self

    @classmethod
    async def get_by_mxid(cls, mxid: UserID, create: bool = True) -> User | None:
        uuid = Puppet.get_id_from_mxid(mxid)
        if not uuid:
            return None
        with contextlib.suppress(KeyError):
            return cls.by_mxid[mxid]

        user = cast(cls, await super().get_by_mxid(mxid))
        if user is not None:
            user._add_to_cache()
            return user

        if create:
            user = cls(mxid=mxid, wazo_uuid=uuid)
            await user.insert()
            user._add_to_cache()
            return user

        return
