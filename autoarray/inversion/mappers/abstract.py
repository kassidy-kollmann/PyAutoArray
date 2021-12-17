import itertools
import numpy as np
from typing import Dict, Optional

from autoconf import cached_property

from autoarray.inversion.linear_obj import LinearObj
from autoarray.inversion.linear_obj import UniqueMappings
from autoarray.structures.grids.two_d.grid_2d_pixelization import Grid2DRectangular
from autoarray.structures.grids.two_d.grid_2d_pixelization import Grid2DDelaunay
from autoarray.structures.grids.two_d.grid_2d_pixelization import Grid2DVoronoi

from autoarray.numba_util import profile_func
from autoarray.inversion.mappers import mapper_util


def mapper(
    source_grid_slim,
    source_pixelization_grid,
    data_pixelization_grid=None,
    hyper_data=None,
):

    if isinstance(source_pixelization_grid, Grid2DRectangular):
        from autoarray.inversion.mappers.rectangular import MapperRectangular

        return MapperRectangular(
            source_grid_slim=source_grid_slim,
            source_pixelization_grid=source_pixelization_grid,
            data_pixelization_grid=data_pixelization_grid,
            hyper_image=hyper_data,
        )
    elif isinstance(source_pixelization_grid, Grid2DDelaunay):
        from autoarray.inversion.mappers.delaunay import MapperDelaunay

        return MapperDelaunay(
            source_grid_slim=source_grid_slim,
            source_pixelization_grid=source_pixelization_grid,
            data_pixelization_grid=data_pixelization_grid,
            hyper_image=hyper_data,
        )
    elif isinstance(source_pixelization_grid, Grid2DVoronoi):
        from autoarray.inversion.mappers.voronoi import MapperVoronoi

        return MapperVoronoi(
            source_grid_slim=source_grid_slim,
            source_pixelization_grid=source_pixelization_grid,
            data_pixelization_grid=data_pixelization_grid,
            hyper_image=hyper_data,
        )


class AbstractMapper(LinearObj):
    def __init__(
        self,
        source_grid_slim,
        source_pixelization_grid,
        data_pixelization_grid=None,
        hyper_image=None,
        profiling_dict: Optional[Dict] = None,
    ):
        """
        To understand a `Mapper`, one must first be familiar with `Pixelization` objects in the `pixelization` package.
        This introduces the following four grids: `data_grid_slim`, `source_grid_slim`, `data_pixelization_grid` and
        `source_pixelization_grid`, whereby the pixelization grid is used to discretize the data grid in the `source`
        frame. If this description is unclear, revert back to the `pixelization` package for further details.

        A `Mapper` provides the index mappings between the pixels on masked data grid (`grid_slim`) and the
        pxelization's pixels (`pixelization_grid`). Indexing of these two grids is the same in both the `data` and
        `source` frames (e.g. the transformation does not change the indexing), meaning that the mapper only needs to
        provide the index mappings between the `data_grid` and `pixelization_grid`, which are derived based on how the
        latter discretizes the former in the `source` frame.

        These mappings are represented in the 1D ndarray `pix_index_for_sub_slim_index`, whereby the index of
        a pixel on the `pixelization_grid` maps to the index of a pixel on the `grid_slim` as follows:

        - pix_index_for_sub_slim_index[0] = 0: the data's 1st sub-pixel maps to the pixelization's 1st pixel.
        - pix_index_for_sub_slim_index[1] = 3: the data's 2nd sub-pixel maps to the pixelization's 4th pixel.
        - pix_index_for_sub_slim_index[2] = 1: the data's 3rd sub-pixel maps to the pixelization's 2nd pixel.

        The mapper allows us to create a mapping matrix, which is a matrix representing the mapping between every
        unmasked pixel of a grid and the pixels of a pixelization. This matrix is the basis of performing an
        `Inversion`, which reconstructed the data using the `source_pixelization_grid`.

        Parameters
        ----------
        pixels
            The number of pixels in the mapper's pixelization.
        source_grid_slim: gridStack
            A stack of grid's which are mapped to the pixelization (includes an and sub grid).
        hyper_image
            A pre-computed hyper-image of the image the mapper is expected to reconstruct, used for adaptive analysis.
        """

        self.source_grid_slim = source_grid_slim
        self.source_pixelization_grid = source_pixelization_grid
        self.data_pixelization_grid = data_pixelization_grid

        self.hyper_image = hyper_image
        self.profiling_dict = profiling_dict

    @property
    def pixels(self):
        return self.source_pixelization_grid.pixels

    @property
    def slim_index_for_sub_slim_index(self):
        return self.source_grid_slim.mask.slim_index_for_sub_slim_index

    @property
    def pix_indexes_for_sub_slim_index(self) -> "PixForSub":
        raise NotImplementedError("pix_index_for_sub_slim_index should be overridden")

    @cached_property
    @profile_func
    def pix_weights_for_sub_slim_index(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def all_sub_slim_indexes_for_pix_index(self):
        """
        Returns the mappings between a pixelization's pixels and the unmasked sub-grid pixels. These mappings
        are determined after the grid is used to determine the pixelization.

        The pixelization's pixels map to different number of sub-grid pixels, thus a list of lists is used to
        represent these mappings.
        """
        all_sub_slim_indexes_for_pix_index = [[] for _ in range(self.pixels)]

        pix_indexes_for_sub_slim_index = self.pix_indexes_for_sub_slim_index.mappings
        sizes = self.pix_indexes_for_sub_slim_index.sizes

        for slim_index, pix_index in enumerate(pix_indexes_for_sub_slim_index):
            for k in range(sizes[slim_index]):
                all_sub_slim_indexes_for_pix_index[pix_index[k]].append(slim_index)

        return all_sub_slim_indexes_for_pix_index

    @cached_property
    @profile_func
    def data_unique_mappings(self):
        """
        The w_tilde formalism requires us to compute an array that gives the unique mappings between the sub-pixels of
        every image pixel to their corresponding pixelization pixels.
        """

        (
            data_to_pix_unique,
            data_weights,
            pix_lengths,
        ) = mapper_util.data_slim_to_pixelization_unique_from(
            data_pixels=self.source_grid_slim.shape_slim,
            pix_indexes_for_sub_slim_index=self.pix_indexes_for_sub_slim_index.mappings,
            pix_indexes_for_sub_slim_sizes=self.pix_indexes_for_sub_slim_index.sizes,
            pix_weights_for_sub_slim_index=self.pix_weights_for_sub_slim_index,
            sub_size=self.source_grid_slim.sub_size,
        )

        return UniqueMappings(
            data_to_pix_unique=data_to_pix_unique,
            data_weights=data_weights,
            pix_lengths=pix_lengths,
        )

    @cached_property
    @profile_func
    def mapping_matrix(self):
        """
        The `mapping_matrix` is a matrix that represents the image-pixel to pixelization-pixel mappings above in a
        2D matrix. It in the following paper as matrix `f` https://arxiv.org/pdf/astro-ph/0302587.pdf.

        A full description is given in `mapper_util.mapping_matrix_from()`.
        """
        return mapper_util.mapping_matrix_from(
            pixel_weights=self.pix_weights_for_sub_slim_index,
            pixels=self.pixels,
            total_mask_sub_pixels=self.source_grid_slim.mask.pixels_in_mask,
            slim_index_for_sub_slim_index=self.slim_index_for_sub_slim_index,
            pix_indexes_for_sub_slim_index=self.pix_indexes_for_sub_slim_index.mappings,
            pix_size_for_sub_slim_index=self.pix_indexes_for_sub_slim_index.sizes,
            sub_fraction=self.source_grid_slim.mask.sub_fraction,
        )

    def pixel_signals_from(self, signal_scale):

        return mapper_util.adaptive_pixel_signals_from(
            pixels=self.pixels,
            signal_scale=signal_scale,
            pixel_weights=self.pix_weights_for_sub_slim_index,
            pix_indexes_for_sub_slim_index=self.pix_indexes_for_sub_slim_index.mappings,
            pix_size_for_sub_slim_index=self.pix_indexes_for_sub_slim_index.sizes,
            slim_index_for_sub_slim_index=self.source_grid_slim.mask.slim_index_for_sub_slim_index,
            hyper_image=self.hyper_image,
        )

    def pix_indexes_for_slim_indexes(self, pix_indexes):

        image_for_source = self.all_sub_slim_indexes_for_pix_index

        if not any(isinstance(i, list) for i in pix_indexes):
            return list(
                itertools.chain.from_iterable(
                    [image_for_source[index] for index in pix_indexes]
                )
            )
        else:
            indexes = []
            for source_pixel_index_list in pix_indexes:
                indexes.append(
                    list(
                        itertools.chain.from_iterable(
                            [
                                image_for_source[index]
                                for index in source_pixel_index_list
                            ]
                        )
                    )
                )
            return indexes

    def reconstruction_from(self, solution_vector):
        """
        Given the solution vector of an inversion (see *inversions.LEq*), determine the reconstructed
        pixelization of the rectangular pixelization by using the mapper.
        """
        raise NotImplementedError()


class PixForSub:
    def __init__(self, mappings, sizes):

        self.mappings = mappings
        self.sizes = sizes
