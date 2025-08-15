from pydantic import BaseModel, Field
from typing import Any, Literal


class DependenciesImplementation(BaseModel):
    """When a Stored Procedure calls another, this dependency will be implemented in subsequent steps. This class represents a placeholder implemented in the current step, but needs to be implemented in subsequent steps. A Stored Procedure should be a Service, not a Repository."""

    procedure_name: str = Field(
        description="The name of the SQL Procedure (dependency) that represent the next class implementation."
    )
    parent_class_name: str = Field(
        description="The name of the current implemented class (parent class) name that is calling the dependency."
    )
    class_to_be_implemented: str = Field(
        description="The name of the placeholder class, representing the SQL Stored Procedure call. It will be implemented in subsequent steps."
    )

    def __init__(
        self,
        procedure_name: str,
        parent_class_name: str,
        class_to_be_implemented: str,
        **kwargs: Any
    ) -> None:
        super().__init__(
            procedure_name=procedure_name,
            parent_class_name=parent_class_name,
            class_to_be_implemented=class_to_be_implemented,
            **kwargs
        )


class ClassImplementation(BaseModel):
    """The class implementation result generated from the SQL Stored Procedure modernization."""

    name: str = Field(
        description="The name of the class implementation, e.g., 'MyClass'."
    )
    namespace: str = Field(description="The namespace of the class implementation.")
    layer: Literal["ServiceLayer", "RepositoryLayer"] = Field(
        description="The layer of the class implementation."
    )
    content: str = Field(description="The content of the class implementation.")
    next_implementation: list[DependenciesImplementation] = Field(
        description="The next implementations that depend on this class."
    )
    type: Literal["Interface", "Implementation"] = Field(
        description="The type of the content in the class implementation, e.g., 'Interface' or 'Implementation'."
    )

    def __init__(
        self,
        name: str,
        content: str,
        namespace: str,
        layer: str,
        next_implementation: list[DependenciesImplementation],
        **kwargs: Any
    ) -> None:
        super().__init__(
            name=name,
            content=content,
            namespace=namespace,
            layer=layer,
            next_implementation=next_implementation,
            **kwargs
        )


class CodeResultModel(BaseModel):
    """Code result content with a list of class implementations."""

    class_implementations: list[ClassImplementation] = Field(
        description="A list of class implementations generated from the procedure analysis."
    )

    def __init__(
        self, class_implementations: list[ClassImplementation], **kwargs: Any
    ) -> None:
        super().__init__(class_implementations=class_implementations, **kwargs)
