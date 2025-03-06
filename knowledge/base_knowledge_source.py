from abc import ABC, abstractmethod


class BaseKnowledgeSource(ABC):
    """
    Base class for knowledge sources which underpin various data fetching tools.
    Subclasses should implement the required methods to fetch and process data.
    """

    @abstractmethod
    def fetch_data(self):
        """
        Fetch data from the knowledge source.

        Returns:
            The fetched data.
        """
        raise NotImplementedError('Subclasses must implement fetch_data method')

    def process_data(self, data):
        """
        Process or transform data as needed.

        Args:
            data: Raw data fetched by the knowledge source.

        Returns:
            Processed data.
        """
        # Default implementation: return data unmodified
        return data
