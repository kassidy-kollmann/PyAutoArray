import numpy as np
from typing import Optional, Tuple

from autoarray.inversion.pixelization.mappers.abstract import AbstractMapper
from autoarray.inversion.pixelization.mappers.mapper_grids import MapperGrids


class MockMapper(AbstractMapper):
    def __init__(
        self,
        source_plane_data_grid=None,
        source_plane_mesh_grid=None,
        hyper_data=None,
        regularization=None,
        pix_sub_weights=None,
        mapping_matrix=None,
        pixel_signals=None,
        parameters=None,
        interpolated_array=None,
    ):

        mapper_grids = MapperGrids(
            source_plane_data_grid=source_plane_data_grid,
            source_plane_mesh_grid=source_plane_mesh_grid,
            hyper_data=hyper_data,
        )

        super().__init__(mapper_grids=mapper_grids, regularization=regularization)

        self._pix_sub_weights = pix_sub_weights

        self._mapping_matrix = mapping_matrix

        self._parameters = parameters

        self._pixel_signals = pixel_signals

        self._interpolated_array = interpolated_array

    def pixel_signals_from(self, signal_scale):
        if self._pixel_signals is None:
            return super().pixel_signals_from(signal_scale=signal_scale)
        return self._pixel_signals

    @property
    def params(self):
        if self._parameters is None:
            return super().params
        return self._parameters

    @property
    def pix_sub_weights(self):
        return self._pix_sub_weights

    @property
    def mapping_matrix(self):
        return self._mapping_matrix

    def interpolated_array_from(
        self,
        values: np.ndarray,
        shape_native: Tuple[int, int] = (401, 401),
        extent: Optional[Tuple[float, float, float, float]] = None,
    ):
        return self._interpolated_array
