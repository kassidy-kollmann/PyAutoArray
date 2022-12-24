import os
from os import path
import numpy as np
import pytest
import shutil

import autoarray as aa
from autoarray import exc

def test__unmasked_grid_sub_1():

    grid_2d_util = aa.util.grid_2d.grid_2d_via_shape_native_from(
        shape_native=(4, 7), pixel_scales=(0.56, 0.56), sub_size=1
    )

    grid_1d_util = aa.util.grid_2d.grid_2d_slim_via_shape_native_from(
        shape_native=(4, 7), pixel_scales=(0.56, 0.56), sub_size=1
    )

    mask = aa.Mask2D.unmasked(shape_native=(4, 7), pixel_scales=(0.56, 0.56))
    mask[0, 0] = True

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert derived_grids.unmasked_grid_sub_1.slim == pytest.approx(grid_1d_util, 1e-4)
    assert derived_grids.unmasked_grid_sub_1.native == pytest.approx(grid_2d_util, 1e-4)
    assert (
        derived_grids.unmasked_grid_sub_1.mask == np.full(fill_value=False, shape=(4, 7))
    ).all()

    mask = aa.Mask2D.unmasked(shape_native=(3, 3), pixel_scales=(1.0, 1.0))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.unmasked_grid_sub_1.native
        == np.array(
            [
                [[1.0, -1.0], [1.0, 0.0], [1.0, 1.0]],
                [[0.0, -1.0], [0.0, 0.0], [0.0, 1.0]],
                [[-1.0, -1.0], [-1.0, 0.0], [-1.0, 1.0]],
            ]
        )
    ).all()

    grid_2d_util = aa.util.grid_2d.grid_2d_via_shape_native_from(
        shape_native=(4, 7), pixel_scales=(0.8, 0.56), sub_size=1
    )

    grid_1d_util = aa.util.grid_2d.grid_2d_slim_via_shape_native_from(
        shape_native=(4, 7), pixel_scales=(0.8, 0.56), sub_size=1
    )

    mask = aa.Mask2D.unmasked(shape_native=(4, 7), pixel_scales=(0.8, 0.56))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert derived_grids.unmasked_grid_sub_1.slim == pytest.approx(grid_1d_util, 1e-4)
    assert derived_grids.unmasked_grid_sub_1.native == pytest.approx(grid_2d_util, 1e-4)

    mask = aa.Mask2D.unmasked(shape_native=(3, 3), pixel_scales=(1.0, 2.0))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.unmasked_grid_sub_1.native
        == np.array(
            [
                [[1.0, -2.0], [1.0, 0.0], [1.0, 2.0]],
                [[0.0, -2.0], [0.0, 0.0], [0.0, 2.0]],
                [[-1.0, -2.0], [-1.0, 0.0], [-1.0, 2.0]],
            ]
        )
    ).all()


def test__masked_grid_sub_1():

    mask = aa.Mask2D.unmasked(shape_native=(3, 3), pixel_scales=(1.0, 1.0))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.masked_grid_sub_1.slim
        == np.array(
            [
                [1.0, -1.0],
                [1.0, 0.0],
                [1.0, 1.0],
                [0.0, -1.0],
                [0.0, 0.0],
                [0.0, 1.0],
                [-1.0, -1.0],
                [-1.0, 0.0],
                [-1.0, 1.0],
            ]
        )
    ).all()

    mask = aa.Mask2D.unmasked(shape_native=(3, 3), pixel_scales=(1.0, 1.0))
    mask[1, 1] = True

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.masked_grid_sub_1.slim
        == np.array(
            [
                [1.0, -1.0],
                [1.0, 0.0],
                [1.0, 1.0],
                [0.0, -1.0],
                [0.0, 1.0],
                [-1.0, -1.0],
                [-1.0, 0.0],
                [-1.0, 1.0],
            ]
        )
    ).all()

    mask = aa.Mask2D.manual(
        mask=np.array([[False, True], [True, False], [True, False]]),
        pixel_scales=(1.0, 1.0),
        origin=(3.0, -2.0),
    )

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.masked_grid_sub_1.slim == np.array([[4.0, -2.5], [3.0, -1.5], [2.0, -1.5]])
    ).all()


def test__edge_grid_sub_1():
    mask = np.array(
        [
            [True, True, True, True, True, True, True, True, True],
            [True, False, False, False, False, False, False, False, True],
            [True, False, True, True, True, True, True, False, True],
            [True, False, True, False, False, False, True, False, True],
            [True, False, True, False, True, False, True, False, True],
            [True, False, True, False, False, False, True, False, True],
            [True, False, True, True, True, True, True, False, True],
            [True, False, False, False, False, False, False, False, True],
            [True, True, True, True, True, True, True, True, True],
        ]
    )

    mask = aa.Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert derived_grids.edge_grid_sub_1.slim[0:11] == pytest.approx(
        np.array(
            [
                [3.0, -3.0],
                [3.0, -2.0],
                [3.0, -1.0],
                [3.0, -0.0],
                [3.0, 1.0],
                [3.0, 2.0],
                [3.0, 3.0],
                [2.0, -3.0],
                [2.0, 3.0],
                [1.0, -3.0],
                [1.0, -1.0],
            ]
        ),
        1e-4,
    )


def test__border_grid_sub_1():
    mask = np.array(
        [
            [True, True, True, True, True, True, True, True, True],
            [True, False, False, False, False, False, False, False, True],
            [True, False, True, True, True, True, True, False, True],
            [True, False, True, False, False, False, True, False, True],
            [True, False, True, False, True, False, True, False, True],
            [True, False, True, False, False, False, True, False, True],
            [True, False, True, True, True, True, True, False, True],
            [True, False, False, False, False, False, False, False, True],
            [True, True, True, True, True, True, True, True, True],
        ]
    )

    mask = aa.Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0))

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert derived_grids.border_grid_sub_1.slim[0:11] == pytest.approx(
        np.array(
            [
                [3.0, -3.0],
                [3.0, -2.0],
                [3.0, -1.0],
                [3.0, -0.0],
                [3.0, 1.0],
                [3.0, 2.0],
                [3.0, 3.0],
                [2.0, -3.0],
                [2.0, 3.0],
                [1.0, -3.0],
                [1.0, 3.0],
            ]
        ),
        1e-4,
    )


def test__masked_grid():

    mask = aa.Mask2D.unmasked(shape_native=(3, 3), pixel_scales=(1.0, 1.0), sub_size=1)
    mask[1, 1] = True

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.masked_grid
        == np.array(
            [
                [1.0, -1.0],
                [1.0, 0.0],
                [1.0, 1.0],
                [0.0, -1.0],
                [0.0, 1.0],
                [-1.0, -1.0],
                [-1.0, 0.0],
                [-1.0, 1.0],
            ]
        )
    ).all()

    mask = aa.Mask2D.manual(
        mask=np.array([[False, True], [True, False], [True, False]]),
        pixel_scales=(1.0, 1.0),
        sub_size=5,
        origin=(3.0, -2.0),
    )

    derived_grids = aa.DerivedGrids2D(mask=mask)

    masked_grid_util = aa.util.grid_2d.grid_2d_slim_via_mask_from(
        mask_2d=mask, pixel_scales=(1.0, 1.0), sub_size=5, origin=(3.0, -2.0)
    )

    assert (derived_grids.masked_grid == masked_grid_util).all()


def test__border_1d_grid():

    mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, False, False, True, True, True, True],
            [True, True, True, True, False, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
        ]
    )

    mask = aa.Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0), sub_size=2)

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.border_grid_1d == np.array([[1.25, -2.25], [1.25, -1.25], [-0.25, 1.25]])
    ).all()

    mask = np.array(
        [
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, False, False, False, True, True],
            [True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True],
        ]
    )

    mask = aa.Mask2D.manual(mask=mask, pixel_scales=(1.0, 1.0), sub_size=2)

    derived_grids = aa.DerivedGrids2D(mask=mask)

    assert (
        derived_grids.border_grid_1d
        == np.array(
            [
                [1.25, -1.25],
                [1.25, 0.25],
                [1.25, 1.25],
                [-0.25, -1.25],
                [-0.25, 1.25],
                [-1.25, -1.25],
                [-1.25, 0.25],
                [-1.25, 1.25],
            ]
        )
    ).all()