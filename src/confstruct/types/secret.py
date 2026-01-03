from typing import Self


class SecretStr(str):  # noqa: SLOT000
    __value__: str

    def __new__(cls, value: str) -> Self:
        obj = super().__new__(cls, "*" * len(value))
        obj.__value__ = value
        return obj

    def get(self) -> str:
        return self.__value__

    def __repr__(self) -> str:
        return f"SecretStr({len(self.__value__) * '*'})"

    @classmethod
    def __validate__(cls, value: str) -> SecretStr:
        return cls(value)
