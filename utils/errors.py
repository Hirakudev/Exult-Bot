from discord import *

from utils.cases import Case




class CaseAlreadyExists(Exception):
    def __init__(self, case:Case):
        super().__init__(f"Case with ID {case.case_id} already exists.")
    ...
class CaseDoesNotExist(Exception):
    def __init__(self, case:Case):
        super().__init__(f"Case with ID {case.case_id} does not exist.")
        ...