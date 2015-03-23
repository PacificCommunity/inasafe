# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Raster Impact on OSM
Buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'

from collections import OrderedDict

from safe.defaults import default_minimum_needs, default_provenance, \
    get_defaults
from safe.definitions import (
    hazard_definition,
    hazard_flood,
    unit_wetdry,
    layer_vector_polygon,
    exposure_definition,
    exposure_population,
    unit_people_per_pixel,
    layer_raster_continuous)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.utilities.i18n import tr


class FloodEvacuationFunctionVectorHazardMetadata(ImpactFunctionMetadata):
    """Metadata for FloodEvacuationFunctionVectorHazard.

    .. versionadded:: 2.1

    We only need to re-implement as_dict(), all other behaviours
    are inherited from the abstract base class.
    """

    @staticmethod
    def as_dict():
        """Return metadata as a dictionary.

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """
        defaults = get_defaults()
        dict_meta = {
                'id': 'FloodEvacuationFunctionVectorHazard',
                'name': tr('Flood Evacuation Function Vector Hazard'),
                'impact': tr('Need evacuation'),
                'title': tr('Need evacuation'),
                'function_type': 'old-style',
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of flood inundation in vector '
                    'format on population.'),
                'detailed_description': tr(
                    'The population subject to inundation is determined '
                    'whether in an area which affected or not. You can also '
                    'set an evacuation percentage to calculate how many '
                    'percent of the total population affected to be '
                    'evacuated. This number will be used to estimate needs'
                    ' based on BNPB Perka 7/2008 minimum bantuan.'),
                'hazard_input': tr(
                    'A hazard vector layer which has attribute affected the '
                    'value is either 1 or 0'),
                'exposure_input': tr(
                    'An exposure raster layer where each cell represent '
                    'population count.'),
                'output': tr(
                    'Vector layer contains people affected and the minimum '
                    'needs based on evacuation percentage.'),
                'actions': tr(
                    'Provide details about how many people would likely need '
                    'to be evacuated, where they are located and what '
                    'resources would be required to support them.'),
                'limitations': [],
                'citations': [],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [hazard_flood],
                        'units': [unit_wetdry],
                        'layer_constraints': [layer_vector_polygon]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_population],
                        'units': [unit_people_per_pixel],
                        'layer_constraints': [layer_raster_continuous]
                    }
                },
                'parameters': OrderedDict([
                    ('evacuation_percentage', 1),  # Percent of affected needing evacuation
                    ('postprocessors', OrderedDict([
                        ('Gender', {'on': True}),
                        ('Age', {
                            'on': True,
                            'params': OrderedDict([
                                ('youth_ratio', defaults['YOUTH_RATIO']),
                                ('adult_ratio', defaults['ADULT_RATIO']),
                                ('elderly_ratio', defaults['ELDERLY_RATIO'])])}),
                        ('MinimumNeeds', {'on': True}),
                    ])),
                    ('minimum needs', default_minimum_needs()),
                    ('provenance', default_provenance())
                ])
        }
        return dict_meta
