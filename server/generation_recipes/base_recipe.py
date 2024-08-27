from abc import ABC, abstractmethod

from server.job_manager import Job


class BaseGenerationRecipe(Job):
    def __init__(self, job_id, **args):
        super().__init__(job_id, **args)

    @staticmethod
    @abstractmethod
    def get_id():
        pass

    @staticmethod
    @abstractmethod
    def name():
        """Name of the recipe"""
        pass

    @staticmethod
    @abstractmethod
    def description():
        """Description of the recipe"""
        pass

