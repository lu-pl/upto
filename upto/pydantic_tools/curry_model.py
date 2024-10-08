"""CurryModel: Constructor for currying a Pydantic Model."""

from typing import Any, Self

from pydantic import BaseModel


class CurryModel[ModelType: BaseModel]:
    """Constructor for currying a Pydantic Model.

    Example:

        class MyModel(BaseModel):
            x: str
            y: int
            z: tuple[str, int]

        curried_model = CurryModel(MyModel)
        curried_model(x="1")
        curried_model(y=2)

        model_instance = curried_model(z=("3", 4))
        print(model_instance)
    """

    def __init__(self, model: type[ModelType], eager: bool = True) -> None:
        self.model = model
        self.eager = eager

        self._kwargs_cache: dict = (
            {k: v.default for k, v in model.model_fields.items() if not v.is_required()}
            if eager
            else {}
        )

    def __repr__(self):  # pragma: no cover
        return f"CurryModel object {self._kwargs_cache}"

    @staticmethod
    def _validate_field[T](model: type[ModelType], field: T, value: Any) -> T:
        """Validate value for a single field given a model."""
        result = model.__pydantic_validator__.validate_assignment(
            model.model_construct(), field, value
        )
        return result

    def __call__(self, **kwargs: Any) -> Self | ModelType:
        for k, v in kwargs.items():
            self._validate_field(self.model, k, v)

        self._kwargs_cache.update(kwargs)

        if self.model.model_fields.keys() == self._kwargs_cache.keys():
            return self.model(**self._kwargs_cache)
        return self
