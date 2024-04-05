import pytest

import autoarray as aa


def test___preloads_used_for_relocated_grid(mask_2d_7x7):
    mesh = aa.mesh.Delaunay()

    relocated_grid = aa.Grid2D.uniform(shape_native=(3, 3), pixel_scales=1.0)

    border_relocator = aa.BorderRelocator(grid=mask_2d_7x7, sub_size=1)

    mapper_grids = mesh.mapper_grids_from(
        border_relocator=border_relocator,
        source_plane_data_grid=relocated_grid,
        source_plane_mesh_grid=relocated_grid,
        preloads=aa.Preloads(relocated_grid=relocated_grid),
    )

    assert mapper_grids.source_plane_data_grid == pytest.approx(relocated_grid, 1.0e-4)
