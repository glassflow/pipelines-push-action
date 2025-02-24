"""
Keep here until we transition to full support of YAML
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, ValidationError, model_validator


class Pipeline(BaseModel):
    name: str
    pipeline_id: str | None = Field(None)
    space_id: str | None = Field(None)
    space_name: str | None = Field(None)
    components: list[Component]

    @model_validator(mode="after")
    def check_space_filled(self):
        """Validate space is filled"""
        if self.space_id is None and self.space_name is None:
            raise ValidationError("`space_id` or `space_name` must be filled")
        if self.pipeline_id is not None and self.space_id is None:
            raise ValidationError("If `pipeline_id` is provided you must specify it's `space_id`")
        return self

    @model_validator(mode="after")
    def check_components(self):
        """Validate pipeline has source, transformer and sink"""

        assert len(self.components) == 3

        source = [c for c in self.components if c.type == "source"]
        transformer = [c for c in self.components if c.type == "transformer"]
        sink = [c for c in self.components if c.type == "sink"]

        assert len(source) == 1
        assert len(transformer) == 1
        assert len(sink) == 1

        assert transformer[0].inputs[0] == source[0].id
        assert sink[0].inputs[0] == transformer[0].id

        return self


class EnvironmentVariable(BaseModel):
    name: str
    value: str | None = Field(None)
    value_secret_ref: str | None = Field(None)

    @model_validator(mode="after")
    def check_filled(self):
        if self.value_secret_ref is None and self.value is None:
            raise ValidationError("value or value_secret_ref must be filled")
        return self


class Requirements(BaseModel):
    path: str | None = Field(None)
    value: str | None = Field(None)

    @model_validator(mode="after")
    def check_filled(self):
        if self.path is None and self.value is None:
            raise ValidationError("Path or value must be filled")
        return self


class Transformation(BaseModel):
    path: str | None = Field(None)
    value: str | None = Field(None)

    @model_validator(mode="after")
    def check_filled(self):
        if self.path is None and self.value is None:
            raise ValidationError("Path or value must be filled")
        return self


class BaseComponent(BaseModel):
    id: str
    name: str | None = Field(None)
    type: str


class TransformerComponent(BaseComponent):
    type: Literal["transformer"]
    requirements: Requirements | None = Field(None)
    transformation: Transformation
    inputs: list[str]
    env_vars: list[EnvironmentVariable] | None = Field(None)


class ConfigParameter(BaseModel):
    value: str | None = Field(None)
    secret_ref: str | None = Field(None)

    @model_validator(mode="after")
    def check_exclusive_fields(self):
        if not (self.value or self.secret_ref):  # Neither is set
            raise ValueError("Either 'value' or 'secret_ref' must be specified.")
        if self.value and self.secret_ref:  # Both are set
            raise ValueError("Only one of 'value' or 'secret_ref' can be specified.")
        return self


class ConfigHeaderParameter(BaseModel):
    name: str
    value: str | None = Field(None)


class ConnectorConfig(
    RootModel[dict[str, Union[ConfigParameter, list[ConfigHeaderParameter]]]]
):
    pass


class SourceComponent(BaseComponent):
    type: Literal["source"]
    kind: str | None = Field(None)
    config: ConnectorConfig | None = Field(None)

    @model_validator(mode="after")
    def check_filled(self):
        if self.kind and not self.config:
            raise ValueError(
                "The 'config' field must be provided when 'kind' is specified. "
                "Please ensure that both 'kind' and 'config' are filled."
            )
        return self


class SinkComponent(BaseComponent):
    type: Literal["sink"]
    kind: str | None = Field(None)
    config: ConnectorConfig | None = Field(None)
    inputs: list[str]

    @model_validator(mode="after")
    def check_filled(self):
        if self.kind and not self.config:
            raise ValueError(
                "The 'config' field must be provided when 'kind' is specified. "
                "Please ensure that both 'kind' and 'config' are filled."
            )
        return self


Component = Annotated[
    Union[TransformerComponent, SourceComponent, SinkComponent],
    Field(discriminator="type"),
]
