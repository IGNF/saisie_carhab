# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaisieCarhab
    Plugin QGIS pour aider à la saisie des entités cartographiques du
    programme CarHab
                             -------------------
        begin                : 2015-07-09
        copyright            : (C) 2015 by IGN
        email                : carhab@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """
    Load SaisieCarhab class from file SaisieCarhab.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .saisie_carhab import SaisieCarhab
    return SaisieCarhab(iface)
