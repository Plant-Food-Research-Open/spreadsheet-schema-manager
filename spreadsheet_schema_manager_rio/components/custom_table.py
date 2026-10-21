from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import rio


T = TypeVar('T')


class CustomTable(rio.Component, Generic[T]):
    rows: list[T] = []
    min_widths: list[int] = []
    row_spacing: float = 0.5
    column_spacing: float = 0.5

    @abstractmethod
    def build_header(self) -> list[rio.Component]:
        pass

    @abstractmethod
    def build_row(self, row: T) -> list[rio.Component]:
        pass

    def set_min_widths(self, row: list[rio.Component]) -> None:
        if self.min_widths:
            for cell, min_width in zip(row, self.min_widths):
                if min_width > 0:
                    cell.min_width = min_width

    def build(self) -> rio.Component:
        header = self.build_header()
        self.set_min_widths(header)

        grid_width = len(header)
        grid = rio.Grid(
            header,
            row_spacing=self.row_spacing,
            column_spacing=self.column_spacing,
        )
        grid.add(rio.Separator(color=self.session.theme.neutral_color), row=1, column=0, width=grid_width)

        for r, row in enumerate(self.rows, start=1):
            content = self.build_row(row)
            self.set_min_widths(content)
            for c, cell in enumerate(content):
                grid.add(cell, row=r*2, column=c)
                grid.add(rio.Separator(color=self.session.theme.neutral_color), row=r*2+1, column=0, width=grid_width)

        return grid
