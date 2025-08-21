from pydantic import BaseModel, Field


class LLMEntityClassResultModel(BaseModel):
    """Model representing the result of an entity class extraction from a database table script."""

    name: str = Field(..., description="Name of the entity class.")
    content: str = Field(..., description="Content of the entity class.")
    signature: str = Field(
        ...,
        description="Signature of the entity class in the format `public <class_name> : <type>`.",
    )
    reference_table: str = Field(
        ..., description="Name of the reference database table for the entity class."
    )
