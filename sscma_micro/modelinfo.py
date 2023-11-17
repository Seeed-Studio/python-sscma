from typing import Dict, Optional


class ModelInfo:
    """
    Represents information about a model.
    """

    def __init__(self, data):
        """
        Initializes a ModelInfo instance.

        Args:
            data (dict): The data containing model information.
        """
        
        if data is None:
            # create a dummy  unknown model
            data = {
                "uuid": 0x00000000,
                "name": "Unknown",
                "version": "0.0.0",
                "catagory": "Unknown",
                "model_type": "Unknown",
                "algoritm": "Unknown",
                "description": "Unknown",
                "image": "",
                "author": "Unknown",
                "token": "",
                "classes": "",
            }
        
        self.data = data

    def __repr__(self):
        """
        Returns a string representation of the ModelInfo instance.

        Returns:
            str: The string representation of the ModelInfo instance.
        """
        return "{} v{}".format(
            self.name,
            self.version
        )
        

    @property
    def uuid(self) -> Optional[str]:
        """
        Returns the UUID of the model if available.

        Returns:
            str or None: The UUID of the model, or None if not available.
        """
        return self.data.get("uuid")

    @property
    def name(self) -> Optional[str]:
        """
        Returns the name of the model if available.

        Returns:
            str or None: The name of the model, or None if not available.
        """
        return self.data.get("name")

    @property
    def version(self) -> Optional[str]:
        """
        Returns the version of the model if available.

        Returns:
            str or None: The version of the model, or None if not available.
        """
        return self.data.get("version")

    @property
    def catagory(self) -> Optional[str]:
        """
        Returns the category of the model if available.

        Returns:
            str or None: The category of the model, or None if not available.
        """
        return self.data.get("catagory")

    @property
    def model_type(self) -> Optional[str]:
        """
        Returns the model type if available.

        Returns:
            str or None: The model type, or None if not available.
        """
        return self.data.get("model_type")

    @property
    def algoritm(self) -> Optional[str]:
        """
        Returns the algorithm of the model if available.

        Returns:
            str or None: The algorithm of the model, or None if not available.
        """
        return self.data.get("algoritm")

    @property
    def description(self) -> Optional[str]:
        """
        Returns the description of the model if available.

        Returns:
            str or None: The description of the model, or None if not available.
        """
        return self.data.get("description")

    @property
    def image(self) -> Optional[str]:
        """
        Returns the image of the model if available.

        Returns:
            str or None: The image of the model, or None if not available.
        """
        return self.data.get("image")

    @property
    def author(self) -> Optional[str]:
        """
        Returns the author of the model if available.

        Returns:
            str or None: The author of the model, or None if not available.
        """
        return self.data.get("author")

    @property
    def token(self) -> Optional[str]:
        """
        Returns the token of the model if available.

        Returns:
            str or None: The token of the model, or None if not available.
        """
        return self.data.get("token")

    @property
    def classes(self) -> Optional[str]:
        """
        Returns the classes of the model if available.

        Returns:
            str or None: The classes of the model, or None if not available.
        """
        return self.data.get("classes")

    @property
    def raw(self) -> Dict:
        """
        Returns the raw data of the model.

        Returns:
            dict: The raw data of the model.
        """
        return self.data
