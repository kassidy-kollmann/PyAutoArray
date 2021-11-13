import numpy as np
from typing import Union

from autoconf import conf
from autoarray.plot.abstract_plotters import Plotter
from autoarray.plot.mat_wrap.visuals import Visuals2D
from autoarray.plot.mat_wrap.include import Include2D
from autoarray.plot.mat_wrap.mat_plot import MatPlot2D
from autoarray.plot.mat_wrap.mat_plot import AutoLabels
from autoarray.structures.arrays.two_d.array_2d import Array2D
from autoarray.inversion.inversion.abstract import AbstractInversion
from autoarray.inversion.plot.mapper_plotters import MapperPlotter


class InversionPlotter(Plotter):
    def __init__(
        self,
        inversion: AbstractInversion,
        mat_plot_2d: MatPlot2D = MatPlot2D(),
        visuals_2d: Visuals2D = Visuals2D(),
        include_2d: Include2D = Include2D(),
    ):
        """
        Plots the attributes of `Inversion` objects using the matplotlib method `imshow()` and many other matplotlib
        functions which customize the plot's appearance.

        The `mat_plot_2d` attribute wraps matplotlib function calls to make the figure. By default, the settings
        passed to every matplotlib function called are those specified in the `config/visualize/mat_wrap/*.ini` files,
        but a user can manually input values into `MatPlot2d` to customize the figure's appearance.

        Overlaid on the figure are visuals, contained in the `Visuals2D` object. Attributes may be extracted from
        the `Array2D` and plotted via the visuals object, if the corresponding entry is `True` in the `Include2D`
        object or the `config/visualize/include.ini` file.

        Parameters
        ----------
        inversion
            The inversion the plotter plots.
        mat_plot_2d
            Contains objects which wrap the matplotlib function calls that make the plot.
        visuals_2d
            Contains visuals that can be overlaid on the plot.
        include_2d
            Specifies which attributes of the `Array2D` are extracted and plotted as visuals.
        """
        super().__init__(
            mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
        )

        self.inversion = inversion

    def get_visuals_2d_for_data(self) -> Visuals2D:
        return self.get_2d.via_mapper_for_data_from(
            mapper=self.inversion.mapper_list[0]
        )

    def as_mapper(self, solution_vector) -> Array2D:
        return self.inversion.mapper_list[0].reconstruction_from(solution_vector)

    def mapper_plotter_from(self, mapper_index):
        return MapperPlotter(
            mapper=self.inversion.mapper_list[mapper_index],
            mat_plot_2d=self.mat_plot_2d,
            visuals_2d=self.visuals_2d,
            include_2d=self.include_2d,
        )

    def figures_2d(self, reconstructed_image: bool = False):
        """
        Plot the model data of an analysis, using the *Fitter* class object.

        The visualization and output type can be fully customized.

        Parameters
        -----------
        fit : autolens.lens.fitting.Fitter
            Class containing fit between the model data and observed lens data (including residual_map, chi_squared_map etc.)
        output_path : str
            The path where the data is output if the output_type is a file format (e.g. png, fits)
        output_format : str
            How the data is output. File formats (e.g. png, fits) output the data to harddisk. 'show' displays the data
            in the python interpreter window.
        """

        if reconstructed_image:

            self.mat_plot_2d.plot_array(
                array=self.inversion.mapped_reconstructed_image,
                visuals_2d=self.get_visuals_2d_for_data(),
                auto_labels=AutoLabels(
                    title="Reconstructed Image", filename="reconstructed_image"
                ),
            )

    def figures_2d_of_mapper(
        self,
        mapper_index: int = 0,
        reconstructed_image: bool = False,
        reconstruction: bool = False,
        errors: bool = False,
        residual_map: bool = False,
        normalized_residual_map: bool = False,
        chi_squared_map: bool = False,
        regularization_weights: bool = False,
    ):
        """
        Plot the model data of an analysis, using the *Fitter* class object.

        The visualization and output type can be fully customized.

        Parameters
        -----------
        fit : autolens.lens.fitting.Fitter
            Class containing fit between the model data and observed lens data (including residual_map, chi_squared_map etc.)
        output_path : str
            The path where the data is output if the output_type is a file format (e.g. png, fits)
        output_format : str
            How the data is output. File formats (e.g. png, fits) output the data to harddisk. 'show' displays the data
            in the python interpreter window.
        """

        mapper_plotter = self.mapper_plotter_from(mapper_index=mapper_index)

        if reconstructed_image:

            self.mat_plot_2d.plot_array(
                array=self.inversion.mapped_reconstructed_image_of_mappers[
                    mapper_index
                ],
                visuals_2d=self.get_visuals_2d_for_data(),
                auto_labels=AutoLabels(
                    title="Reconstructed Image", filename="reconstructed_image"
                ),
            )

        if reconstruction:

            vmax_custom = False

            if "vmax" in self.mat_plot_2d.cmap.kwargs:
                if self.mat_plot_2d.cmap.kwargs["vmax"] is None:

                    reconstruction_vmax_factor = conf.instance["visualize"]["general"][
                        "inversion"
                    ]["reconstruction_vmax_factor"]

                    self.mat_plot_2d.cmap.kwargs["vmax"] = (
                        reconstruction_vmax_factor
                        * np.max(self.inversion.reconstruction)
                    )
                    vmax_custom = True

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.reconstruction_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(
                    title="Source Inversion", filename="reconstruction"
                ),
            )

            if vmax_custom:
                self.mat_plot_2d.cmap.kwargs["vmax"] = None

        if errors:

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.errors_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(title="Errors", filename="errors"),
            )

        if residual_map:

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.residual_map_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(title="Residual Map", filename="residual_map"),
            )

        if normalized_residual_map:

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.normalized_residual_map_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(
                    title="Normalized Residual Map", filename="normalized_residual_map"
                ),
            )

        if chi_squared_map:

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.chi_squared_map_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(
                    title="Chi-Squared Map", filename="chi_squared_map"
                ),
            )

        if regularization_weights:

            mapper_plotter.plot_source_from(
                source_pixelization_values=self.inversion.regularization_weights_of_mappers[
                    mapper_index
                ],
                auto_labels=AutoLabels(
                    title="Regularization weight_list",
                    filename="regularization_weights",
                ),
            )

    def subplot_of_mapper(
        self, mapper_index: int = 0, auto_filename: str = "subplot_inversion"
    ):

        self.open_subplot_figure(number_subplots=6)

        self.figures_2d_of_mapper(mapper_index=mapper_index, reconstructed_image=True)
        self.figures_2d_of_mapper(mapper_index=mapper_index, reconstruction=True)
        self.figures_2d_of_mapper(mapper_index=mapper_index, errors=True)
        self.figures_2d_of_mapper(mapper_index=mapper_index, residual_map=True)
        self.figures_2d_of_mapper(
            mapper_index=mapper_index, normalized_residual_map=True
        )
        self.figures_2d_of_mapper(mapper_index=mapper_index, chi_squared_map=True)

        self.mat_plot_2d.output.subplot_to_figure(
            auto_filename=f"{auto_filename}_{mapper_index}"
        )

        self.close_subplot_figure()
