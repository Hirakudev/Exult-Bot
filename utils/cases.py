import datetime
from uuid import *
from typing import *

import discord
from bot import ExultBot
from utils import CasesDB, CaseAlreadyExists, CaseDoesNotExist
class CaseBase:
    """
    Base Class for all cases
    """
    def __init__(
        self,
        client:ExultBot = ...,
        case_id:UUID = ...,
        user:discord.Member = ...,
        moderator:discord.Member = ...,
        reason: str = ...,
        created_at: datetime.datetime = ...,
        last_updated:datetime.datetime = ...,
        expires: datetime.datetime = ...,
        **kwargs
    ):
        self.case_id = case_id if case_id else uuid4()
        self.case_type = self.__class__.__name__
        self.guild = user.guild
        self.moderator = moderator
        self.user = user
        self.reason = reason
        self.created_at = created_at
        self.last_updated = last_updated
        self.expires = expires
        self.kwargs = kwargs
        self.client = client
        self._cases = CasesDB(client)
        self.__dict__ = {
            "case_id": self.case_id,
            "case_type": self.case_type,
            "guild_id": self.guild_id,
            "user_id": self.user_id,
            "moderator_id": self.moderator_id,
            "reason": self.reason,
            "created_at": self.created_at,
            "expires": self.expires,
            "kwargs": self.kwargs,
        }
    
    def __str__(self) -> str:
        return f"""
*Case Information*

Case ID - {self.case_id}
Case Type - {self.case_type}
Reason - {self.reason}
Guild ID - {self.guild.id}
Guild Name - {self.guild.name}
User ID - {self.user_id}
Moderator ID - {self.moderator_id}
Created At - <t:{int(self.created_at.timestamp)}:f>
Expires - <t:{self.expires}:f>
Data - {self.kwargs}

"""



class Case(CaseBase):
    """
    Class representing a generic case \n
    Warns are a good example of a generic case
    """
    
    async def send_case(self):
        """
        Sends the case to the database\n

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel
        
        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database
        """
        
            
        
        if await self._cases.check_case_exists(self.case_id):
            raise CaseAlreadyExists(self)
        return await self._cases.add_case(
            self.case_type,
            self.guild_id,
            self.user_id,
            self.moderator_id,
            self.reason,
            self.created_at,
            self.expires,
            return_case = True
        )

    async def delete_case(self):
        """
        Deletes the case from the database

        Raises
        -------
        :class:`CaseDoesNotExist`
            Case this case doesn't exist in the database
        """
        if not await self._cases.check_case_exists(self.case_id):
            raise CaseDoesNotExist(self)
        await self._cases.delete_case(self.case_id)
    
    async def update_case(
        self,
        *,
        reason: str = None,
    ):
        """
        Updates the case in the database

        Raises
        -------
        :class:`CaseDoesNotExist`
            Case this case doesn't exist in the database
        """
        if not reason: return
        self.reason = reason
        if not await self._cases.check_case_exists(self.case_id):
            raise CaseDoesNotExist(self)
        await self._cases.update_case(self.case_id, self.reason)
        

class Kick(Case):
    """
    A class representing a kick case
    """
    async def confirm_action(self) -> Dict[str, Any] | None:
        """
        Quick action function that will send the case to the database then kick the user.

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel

        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database

        """
        
        await self.moderator.guild.kick(self.user, reason=self.reason)
        return await self.send_case()
    

class Ban(Case):    
    """
    class representing a ban case
    """
    async def confirm_action(self):
        """
        Quick action function that will send the case to the database then ban the user.

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel

        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database

        """
        
        await self.moderator.guild.ban(self.user, reason=self.reason)
        return await self.send_case()


class Mute(Case):
    """
    class representing a mute case
    """

    async def confirm_action(self):
        """
        Quick action function that will send the case to the database then mute the user.

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel

        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database

        """
        await self.user.timeout(self.expires, reason=self.reason)
        return await self.send_case()
        ...


class Unban(Case):
    """
    class representing a unban case
    """
    async def confirm_action(self):
        """
        Quick action function that will send the case to the database then unban the user.

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel

        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database

        """
        await self.moderator.guild.unban(self.user, reason=self.reason)
        return await self.send_case()

class Unmute(Case):
    """
    class representing a unmute case
    """
    async def confirm_action(self):
        """
        Quick action function that will send the case to the database then unmute the user.

        Returns
        --------
        :class:`Dict[str, Any]`
            Dictionary containing the case number and the channel_id of the moderation log channel

        Raises
        -------
        :class:`CaseAlreadyExists`
            Case already exists in the database

        """
        await self.user.timeout(None)
        return await self.send_case()
