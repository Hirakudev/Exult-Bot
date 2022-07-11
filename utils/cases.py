import datetime

class CaseBase:
    """
    A class representing a generic case.
    :param case_type: str - The Unique ID of the case
    :param guild_id: int - The ID of the guild the case is in
    :param user_id: int - The ID of the user the case is for
    :param moderator_id: int - The ID of the moderator who created the case
    :param reason: str - The reason for the case
    :param created_at: datetime.datetime - The time the case was created
    :param expires: datetime.datetime - The time the case expires
    :param kwargs: dict - Any additional data to be stored with the case

    """
    def __init__(
        self,
        case_type: str,
        guild_id: int,
        user_id: int,
        moderator_id: int,
        reason: str,
        created_at: datetime.datetime,
        expires: datetime.datetime = None,
        **kwargs
    ):
        self.case_type = case_type
        self.guild_id = guild_id
        self.user_id = user_id
        self.moderator_id = moderator_id
        self.reason = reason
        self.created_at = created_at
        self.expires = expires
        self.kwargs = kwargs
        