# coding=utf-8
"""InaSAFE Dock."""

import os
import shutil
import logging
import codecs

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, pyqtSlot
from qgis.core import (
    QgsRectangle,
    QgsGeometry,
    QgsMapLayer,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QGis)

from safe.definitions.layer_purposes import (
    layer_purpose_exposure_impacted,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_aggregation_impacted,
    layer_purpose_analysis_impacted,
    layer_purpose_exposure_breakdown,
)
from safe.definitions.constants import (
    inasafe_keyword_version_key,
    HAZARD_EXPOSURE_VIEW,
    HAZARD_EXPOSURE_BOUNDINGBOX,
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_CODE,
    ANALYSIS_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP,
    PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT,
    PREPARE_FAILED_BAD_LAYER,
    PREPARE_SUCCESS,
)
from safe.defaults import supporters_logo_path
from safe.report.impact_report import ImpactReport
from safe.utilities.gis import wkt_to_rectangle
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import (
    get_error_message,
    add_ordered_combo_item,
    is_keyword_version_supported,
)
from safe.utilities.settings import setting, set_setting
from safe.utilities.resources import get_ui_class
from safe.utilities.qgis_utilities import (
    display_critical_message_bar,
    display_warning_message_bar,
    display_information_message_bar)
from safe.utilities.extent import Extent
from safe.utilities.qt import disable_busy_cursor, enable_busy_cursor

from safe.common.version import get_version
from safe.common.signals import (send_static_message, send_error_message)
from safe import messaging as m
from safe.messaging import styles
from safe.common.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError,
    InvalidParameterError,
    HashNotFoundError,
    MetadataReadError)
from safe.impact_function.impact_function import ImpactFunction
from safe.gui.tools.about_dialog import AboutDialog
from safe.gui.tools.help_dialog import HelpDialog
from safe.gui.widgets.message import (
    show_no_keywords_message,
    show_keyword_version_message,
    getting_started_message,
    no_overlap_message,
    ready_message,
    enable_messaging)
from safe.gui.analysis_utilities import (
    generate_impact_report,
    generate_impact_map_report,
    add_impact_layers_to_canvas,
    add_debug_layers_to_canvas)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
WARNING_STYLE = styles.RED_LEVEL_4_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.GREEN_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()

FORM_CLASS = get_ui_class('dock_base.ui')

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyArgumentList
# noinspection PyUnresolvedReferences
class Dock(QtGui.QDockWidget, FORM_CLASS):
    """Dock implementation class for the inaSAFE plugin."""

    def __init__(self, iface):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        :param iface: A QGisAppInterface instance we use to access QGIS via.
        :type iface: QgsAppInterface

        .. note:: We use the multiple inheritance approach from Qt4 so that
            for elements are directly accessible in the form context and we can
            use autoconnect to set up slots. See article below:
            http://doc.qt.nokia.com/4.7-snapshot/designer-using-a-ui-file.html
        """
        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.show_question_button.setVisible(False)
        self.progress_bar.hide()
        enable_messaging(self.results_webview, self)
        self.inasafe_version = get_version()

        self.set_dock_title()

        # Save reference to the QGIS interface
        self.iface = iface

        self.impact_function = None
        self.keyword_io = KeywordIO()
        self.state = None
        self.extent = Extent(self.iface)
        self.composer = None
        self.composition = None
        self.map_canvas = None

        # Flag used to prevent recursion and allow bulk loads of layers to
        # trigger a single event only
        self.get_layers_lock = False
        # Flag so we can see if the dock is busy processing
        self.busy = False

        self.show_only_visible_layers_flag = None
        self.set_layer_from_title_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.map_canvas = None
        self.developer_mode = None
        self.organisation_logo_path = None

        self.print_button.setEnabled(False)

        self.setup_button_connectors()

        self.iface.layerSavedAs.connect(self.save_auxiliary_files)

        canvas = self.iface.mapCanvas()

        # Current aggregation layer
        self._aggregation = None

        # Enable on the fly projection by default
        canvas.setCrsTransformEnabled(True)
        self.connect_layer_listener()
        self.question_group.setEnabled(False)
        self.question_group.setVisible(False)

        self.read_settings()  # get_project_layers called by this

        # debug_mode is a check box to know if we run the IF with debug mode.
        self.debug_mode.setVisible(self.developer_mode)
        self.debug_mode.setChecked(False)

        # Check the validity
        self.validate_impact_function()

    @property
    def aggregation(self):
        """Property for the current aggregation layer.

        :return: The aggregation layer or None.
        :rtype: QgsVectorLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for the current aggregation layer.

        :param layer: The current aggregation layer.
        :type layer: QgsVectorLayer
        """
        use_selected_only = setting('useSelectedFeaturesOnly', False, bool)

        # We need to disconnect first.
        if self._aggregation and use_selected_only:
            self._aggregation.selectionChanged.disconnect(
                self.validate_impact_function)

        self._aggregation = layer

        if use_selected_only and layer:
            self._aggregation.selectionChanged.connect(
                self.validate_impact_function)

    def set_dock_title(self):
        """Set the title of the dock using the current version of InaSAFE."""
        self.setWindowTitle(self.tr('InaSAFE %s' % self.inasafe_version))

    def setup_button_connectors(self):
        """Setup signal/slot mechanisms for dock buttons."""
        self.help_button.clicked.connect(self.show_help)
        self.run_button.clicked.connect(self.accept)
        self.about_button.clicked.connect(self.about)
        self.print_button.clicked.connect(self.print_map)

    def about(self):
        """Open the About dialog."""
        # noinspection PyTypeChecker
        dialog = AboutDialog(self)
        dialog.show()

    def _show_organisation_logo(self):
        """Show the organisation logo in the dock if possible."""
        dock_width = float(self.width())
        # Don't let the image be more tha 100px height
        maximum_height = 100.0  # px
        pixmap = QtGui.QPixmap(self.organisation_logo_path)
        if pixmap.height() < 1 or pixmap.width() < 1:
            return

        height_ratio = maximum_height / pixmap.height()
        maximum_width = int(pixmap.width() * height_ratio)
        # Don't let the image be more than the dock width wide
        if maximum_width > dock_width:
            width_ratio = dock_width / float(pixmap.width())
            maximum_height = int(pixmap.height() * width_ratio)
            maximum_width = dock_width
        too_high = pixmap.height() > maximum_height
        too_wide = pixmap.width() > dock_width
        if too_wide or too_high:
            pixmap = pixmap.scaled(
                maximum_width, maximum_height, Qt.KeepAspectRatio)
        self.organisation_logo.setMaximumWidth(maximum_width)
        # We have manually scaled using logic above
        self.organisation_logo.setScaledContents(False)
        self.organisation_logo.setPixmap(pixmap)
        self.organisation_logo.show()

    def read_settings(self):
        """Set the dock state from QSettings.

        Do this on init and after changing options in the options dialog.
        """
        extent = setting('user_extent', None, str)
        if extent:
            extent = QgsGeometry.fromWkt(extent)
            if not extent.isGeosValid():
                extent = None

        crs = setting('user_extent_crs', None, str)
        if crs:
            crs = QgsCoordinateReferenceSystem(crs)
            if not crs.isValid():
                crs = None

        mode = setting('analysis_extents_mode', HAZARD_EXPOSURE_VIEW)
        if crs and extent and mode == HAZARD_EXPOSURE_BOUNDINGBOX:
            self.extent.set_user_extent(extent, crs)

        # It's better to set the show_rubber_bands after setting the user
        # extent.
        self.extent.show_rubber_bands = setting(
            'showRubberBands', False, bool)

        flag = setting('visibleLayersOnlyFlag', True, bool)
        self.show_only_visible_layers_flag = flag

        flag = setting('set_layer_from_title_flag', True, bool)
        self.set_layer_from_title_flag = flag

        self.zoom_to_impact_flag = setting('setZoomToImpactFlag', True, bool)

        # whether exposure layer should be hidden after model completes
        self.hide_exposure_flag = setting('setHideExposureFlag', False, bool)

        # whether to show or not dev only options
        self.developer_mode = setting('developer_mode', False, bool)

        # whether to show or not a custom Logo
        flag = setting('organisation_logo_path', supporters_logo_path(), str)
        self.organisation_logo_path = flag

        # Changed default to False for new users in 3.2 - see #2171
        show_logos_flag = setting(
            'showOrganisationLogoInDockFlag', False, bool)

        # Flag to check valid organization logo
        invalid_logo_size = False
        logo_not_exist = False

        if self.organisation_logo_path:
            dock_width = float(self.width())

            # Dont let the image be more tha 100px hight
            maximum_height = 100.0  # px
            pixmap = QtGui.QPixmap(self.organisation_logo_path)
            # it will throw Overflow Error if pixmap.height() == 0
            if pixmap.height() > 0:

                height_ratio = maximum_height / pixmap.height()
                maximum_width = int(pixmap.width() * height_ratio)

                # Don't let the image be more than the dock width wide
                if maximum_width > dock_width:
                    width_ratio = dock_width / float(pixmap.width())
                    maximum_height = int(pixmap.height() * width_ratio)
                    maximum_width = dock_width

                too_high = pixmap.height() > maximum_height
                too_wide = pixmap.width() > dock_width

                if too_wide or too_high:
                    pixmap = pixmap.scaled(
                        maximum_width, maximum_height, Qt.KeepAspectRatio)

                self.organisation_logo.setMaximumWidth(maximum_width)
                # We have manually scaled using logic above
                self.organisation_logo.setScaledContents(False)
                self.organisation_logo.setPixmap(pixmap)
            else:
                # handle zero pixmap height and or nonexistent files
                if not os.path.exists(self.organisation_logo_path):
                    logo_not_exist = True
                else:
                    invalid_logo_size = True

        if (self.organisation_logo_path and show_logos_flag and
                not invalid_logo_size and not logo_not_exist):
            self._show_organisation_logo()
        else:
            self.organisation_logo.hide()

        # RM: this is a fix for nonexistent organization logo or zero height
        if logo_not_exist:
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE %s' % self.inasafe_version),
                self.tr(
                    'The file for organization logo in %s doesn\'t exists. '
                    'Please check in Plugins -> InaSAFE -> Options that your '
                    'paths are still correct and update them if needed.' %
                    self.organisation_logo_path
                ), QtGui.QMessageBox.Ok)
        if invalid_logo_size:
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE %s' % self.inasafe_version),
                self.tr(
                    'The file for organization logo has zero height. Please '
                    'provide valid file for organization logo.'
                ), QtGui.QMessageBox.Ok)
        if logo_not_exist or invalid_logo_size:
            set_setting('organisation_logo_path', supporters_logo_path())

    def connect_layer_listener(self):
        """Establish a signal/slot to listen for layers loaded in QGIS.

        ..seealso:: disconnect_layer_listener
        """
        registry = QgsMapLayerRegistry.instance()
        registry.layersWillBeRemoved.connect(self.get_layers)
        registry.layersAdded.connect(self.get_layers)
        registry.layersRemoved.connect(self.get_layers)

        self.iface.mapCanvas().layersChanged.connect(self.get_layers)
        self.iface.currentLayerChanged.connect(self.layer_changed)

        if not self._aggregation:
            self.iface.mapCanvas().extentsChanged.connect(
                self.validate_impact_function)

    # pylint: disable=W0702
    def disconnect_layer_listener(self):
        """Destroy the signal/slot to listen for layers loaded in QGIS.

        ..seealso:: connect_layer_listener
        """
        registry = QgsMapLayerRegistry.instance()
        registry.layersWillBeRemoved.disconnect(self.get_layers)
        registry.layersAdded.disconnect(self.get_layers)
        registry.layersRemoved.disconnect(self.get_layers)

        self.iface.mapCanvas().layersChanged.disconnect(self.get_layers)
        self.iface.currentLayerChanged.disconnect(self.layer_changed)

        if not self._aggregation:
            self.iface.mapCanvas().extentsChanged.disconnect(
                self.validate_impact_function)

    @pyqtSlot(QgsMapLayer, str)
    def save_auxiliary_files(self, layer, destination):
        """Save auxiliary files when using the 'save as' function.

        If some auxiliary files (.xml, .json) exist, this function will
        copy them when the 'save as' function is used on the layer.

        :param layer: The layer which has been saved as.
        :type layer: QgsMapLayer

        :param destination: The new filename of the layer.
        :type destination: str
        """

        enable_busy_cursor()

        auxiliary_files = ['xml', 'json']

        for auxiliary_file in auxiliary_files:
            source_basename = os.path.splitext(layer.source())[0]
            source_file = "%s.%s" % (source_basename, auxiliary_file)

            destination_basename = os.path.splitext(destination)[0]
            destination_file = "%s.%s" % (destination_basename, auxiliary_file)

            # noinspection PyBroadException,PyBroadException
            try:
                if os.path.isfile(source_file):
                    shutil.copy(source_file, destination_file)

            except (OSError, IOError):
                display_critical_message_bar(
                    title=self.tr('Error while saving'),
                    message=self.tr(
                        'The destination location must be writable.'))

            except Exception:  # pylint: disable=broad-except
                display_critical_message_bar(
                    title=self.tr('Error while saving'),
                    message=self.tr('Something went wrong.'))

        disable_busy_cursor()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_hazard_layer_combo_currentIndexChanged(self, index):
        """Automatic slot executed when the Hazard combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected hazard layer.
        """
        # Add any other logic you might like here...
        del index
        self.toggle_aggregation_layer_combo()
        self.validate_impact_function()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_exposure_layer_combo_currentIndexChanged(self, index):
        """Automatic slot executed when the Exposure combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected exposure layer.
        """
        # Add any other logic you might like here...
        del index
        self.toggle_aggregation_layer_combo()
        self.validate_impact_function()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_aggregation_layer_combo_currentIndexChanged(self, index):
        """Automatic slot executed when the Aggregation combo is changed.

        :param index: The index number of the selected exposure layer.
        :type index: int
        """
        if index == 0:
            # No aggregation layer, we should display the user requested extent
            self.aggregation = None

            extent = setting('user_extent', None, str)
            if extent:
                extent = QgsGeometry.fromWkt(extent)
                if not extent.isGeosValid():
                    extent = None

            crs = setting('user_extent_crs', None, str)
            if crs:
                crs = QgsCoordinateReferenceSystem(crs)
                if not crs.isValid():
                    crs = None

            mode = setting('analysis_extents_mode', HAZARD_EXPOSURE_VIEW)
            if crs and extent and mode == HAZARD_EXPOSURE_BOUNDINGBOX:
                self.extent.set_user_extent(extent, crs)

        else:
            # We have one aggregation layer. We should not display the user
            # extent.
            self.extent.clear_user_analysis_extent()
            self.aggregation = self.get_aggregation_layer()

        self.validate_impact_function()

    def toggle_aggregation_layer_combo(self):
        """Toggle the aggregation combo enabled status.

        Whether the combo is toggled on or off will depend on the current dock
        status.
        """
        selected_hazard_layer = self.get_hazard_layer()
        selected_exposure_layer = self.get_exposure_layer()

        # more than 1 because No aggregation is always there
        if ((self.aggregation_layer_combo.count() > 1) and
                (selected_hazard_layer is not None) and
                (selected_exposure_layer is not None)):
            self.aggregation_layer_combo.setEnabled(True)
        else:
            self.aggregation_layer_combo.setCurrentIndex(0)
            self.aggregation_layer_combo.setEnabled(False)

    def unblock_signals(self):
        """Let the combos listen for event changes again."""
        self.aggregation_layer_combo.blockSignals(False)
        self.exposure_layer_combo.blockSignals(False)
        self.hazard_layer_combo.blockSignals(False)

    def block_signals(self):
        """Prevent the combos and dock listening for event changes."""
        self.disconnect_layer_listener()
        self.aggregation_layer_combo.blockSignals(True)
        self.exposure_layer_combo.blockSignals(True)
        self.hazard_layer_combo.blockSignals(True)

    # noinspection PyUnusedLocal
    @pyqtSlot('QgsMapLayer')
    def get_layers(self, *args):
        """Obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate hazard_layer_combo,
        exposure_layer_combo and aggregation_layer_combo on the dialog
        with a list of available layers.

        Only **polygon vector** layers will be added to the aggregate list.

        :param args: Arguments that may have been passed to this slot.
            Typically a list of layers, but depends on which slot or function
            called this function.
        :type args: list

        ..note:: \*args is only used for debugging purposes.
        """
        _ = args
        # Prevent recursion
        if self.get_layers_lock:
            return

        # Map registry may be invalid if QGIS is shutting down
        registry = QgsMapLayerRegistry.instance()
        canvas_layers = self.iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
        if len(layers) == 0:
            send_static_message(self, getting_started_message())
            return

        self.get_layers_lock = True

        # Make sure this comes after the checks above to prevent signal
        # disconnection without reconnection
        self.block_signals()
        self.save_state()
        self.hazard_layer_combo.clear()
        self.exposure_layer_combo.clear()
        self.aggregation_layer_combo.clear()

        for layer in layers:
            if (self.show_only_visible_layers_flag and
                    (layer not in canvas_layers)):
                continue

            # .. todo:: check raster is single band
            #    store uuid in user property of list widget for layers

            name = layer.name()
            source = layer.id()
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename

            # noinspection PyBroadException
            try:
                title = self.keyword_io.read_keywords(layer, 'title')
            except (NoKeywordsFoundError,
                    KeywordNotFoundError, MetadataReadError):
                # Skip if there are no keywords at all, or missing keyword
                continue
            except:  # pylint: disable=W0702
                pass
            else:
                # Lookup internationalised title if available
                title = self.tr(title)
            # Register title with layer
            if title and self.set_layer_from_title_flag:
                layer.setLayerName(title)

            # Find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            # noinspection PyBroadException
            try:
                layer_purpose = self.keyword_io.read_keywords(
                    layer, 'layer_purpose')
                keyword_version = str(self.keyword_io.read_keywords(
                    layer, inasafe_keyword_version_key))
                if not is_keyword_version_supported(keyword_version):
                    continue
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            if layer_purpose == 'hazard':
                add_ordered_combo_item(
                    self.hazard_layer_combo, title, source)
            elif layer_purpose == 'exposure':
                add_ordered_combo_item(
                    self.exposure_layer_combo, title, source)
            elif layer_purpose == 'aggregation':
                add_ordered_combo_item(
                    self.aggregation_layer_combo, title, source)

        self.unblock_signals()
        # handle the aggregation_layer_combo combo
        self.aggregation_layer_combo.insertItem(0, self.tr('Entire area'))
        self.aggregation_layer_combo.setCurrentIndex(0)
        self.toggle_aggregation_layer_combo()

        self.restore_state()
        self.question_group.setEnabled(True)
        self.question_group.setVisible(True)
        self.show_question_button.setVisible(False)
        # Note: Don't change the order of the next two lines otherwise there
        # will be a lot of unneeded looping around as the signal is handled
        self.connect_layer_listener()
        self.get_layers_lock = False
        # ensure the dock keywords info panel is updated
        # make sure to do this after the lock is released!
        self.layer_changed(self.iface.activeLayer())

    def get_hazard_layer(self):
        """Get the QgsMapLayer currently selected in the hazard combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for hazard
        and return it as a QgsMapLayer.

        :returns: The currently selected map layer in the hazard combo.
        :rtype: QgsMapLayer

        """
        index = self.hazard_layer_combo.currentIndex()
        if index < 0:
            return None

        layer_id = self.hazard_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_exposure_layer(self):
        """Get the QgsMapLayer currently selected in the exposure combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for exposure
        and return it as a QgsMapLayer.

        :returns: Currently selected map layer in the exposure combo.
        :rtype: QgsMapLayer
        """
        index = self.exposure_layer_combo.currentIndex()
        if index < 0:
            return None

        layer_id = self.exposure_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_aggregation_layer(self):
        """Get the QgsMapLayer currently selected in the post processing combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for post
        processing combo return it as a QgsMapLayer.

        :returns: None if no aggregation is selected or aggregation_layer_combo
            is disabled, otherwise a polygon layer.
        :rtype: QgsVectorLayer or None
        """
        index = self.aggregation_layer_combo.currentIndex()
        if index < 0:
            return None

        layer_id = self.aggregation_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    @pyqtSlot('bool')
    def toggle_rubber_bands(self, flag):
        """Disabled/enable the rendering of rubber bands.

        This slot is called from the button.

        :param flag: Flag to indicate if drawing of bands is active.
        :type flag: bool
        """
        self.extent.show_rubber_bands = flag
        set_setting('showRubberBands', flag)

    def progress_callback(self, current_value, maximum_value, message=None):
        """GUI based callback implementation for showing progress.

        :param current_value: Current progress.
        :type current_value: int

        :param maximum_value: Maximum range (point at which task is complete.
        :type maximum_value: int

        :param message: Optional message dictionary to containing content
            we can display to the user. See safe.definitions.analysis_steps
            for an example of the expected format
        :type message: dict
        """
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(
            self.tr('Analysis status'), **INFO_STYLE))
        if message is not None:
            report.add(m.ImportantText(message['name']))
            report.add(m.Paragraph(message['description']))
        report.add(self.impact_function.performance_log_message())
        send_static_message(self, report)
        self.progress_bar.setMaximum(maximum_value)
        self.progress_bar.setValue(current_value)
        QtGui.QApplication.processEvents()

    def accept(self):
        """Execute analysis when run button is clicked."""
        # Start the analysis
        self.impact_function = self.validate_impact_function()
        if not self.impact_function:
            # This should not happen as the "accept" button should disabled if
            # the impact function is not ready.
            LOGGER.info(tr('The impact function should not have been ready.'))
            return

        self.show_busy()
        self.impact_function.callback = self.progress_callback
        self.impact_function.debug_mode = self.debug_mode.isChecked()
        try:
            status, message = self.impact_function.run()
        except:
            # We have an exception only if we are in debug mode.
            # We want to display the datastore and then
            # we want to re-raise it to get the first aid plugin popup.
            add_debug_layers_to_canvas(self.impact_function)
            disable_busy_cursor()
            raise
        if status == ANALYSIS_FAILED_BAD_INPUT:
            self.hide_busy()
            LOGGER.info(tr(
                'The impact function could not run because of the inputs.'))
            send_error_message(self, message)
            LOGGER.info(message.to_text())
            return status, message
        elif status == ANALYSIS_FAILED_BAD_CODE:
            self.hide_busy()
            LOGGER.exception(tr(
                'The impact function could not run because of a bug.'))
            LOGGER.exception(message.to_text())
            send_error_message(self, message)

            # Even if we are not in debug mode, as we got an exception, we
            # display the debug group.
            add_debug_layers_to_canvas(self.impact_function)
            return status, message

        LOGGER.info(tr('The impact function could run without errors.'))

        # Add result layer to QGIS
        add_impact_layers_to_canvas(self.impact_function, self.iface)

        if setting('generate_report', True, bool):
            # Generate impact report
            error_code, message = generate_impact_report(
                self.impact_function, self.iface)

            if error_code == ImpactReport.REPORT_GENERATION_FAILED:
                LOGGER.info(tr(
                    'The impact report could not be generated.'))
                send_error_message(self, message)
                LOGGER.info(message.to_text())
                return ANALYSIS_FAILED_BAD_CODE, message

            error_code, message = generate_impact_map_report(
                self.impact_function, self.iface)

            if error_code == ImpactReport.REPORT_GENERATION_FAILED:
                LOGGER.info(tr(
                    'The impact report could not be generated.'))
                send_error_message(self, message)
                LOGGER.info(message.to_text())
                return ANALYSIS_FAILED_BAD_CODE, message

        if self.zoom_to_impact_flag:
            self.iface.zoomToActiveLayer()

        if self.impact_function.debug_mode:
            add_debug_layers_to_canvas(self.impact_function)

        if self.hide_exposure_flag:
            legend = self.iface.legendInterface()
            qgis_exposure = self.get_exposure_layer()
            legend.setLayerVisible(qgis_exposure, False)

        self.extent.set_last_analysis_extent(
            self.impact_function.analysis_extent,
            self.get_exposure_layer().crs())

        self.hide_busy()
        self.impact_function = None
        return ANALYSIS_SUCCESS, None

    def show_help(self):
        """Open the help dialog."""
        # noinspection PyTypeChecker
        dialog = HelpDialog(self)
        dialog.show()

    def show_busy(self):
        """Hide the question group box and enable the busy cursor."""
        self.progress_bar.show()
        self.question_group.setEnabled(False)
        self.question_group.setVisible(False)
        enable_busy_cursor()
        self.repaint()
        QtGui.qApp.processEvents()
        self.busy = True

    def hide_busy(self):
        """A helper function to indicate processing is done."""
        self.progress_bar.hide()
        self.show_question_button.setVisible(True)
        self.question_group.setEnabled(True)
        self.question_group.setVisible(False)

        # We check if we can run an IF
        self.validate_impact_function()

        self.repaint()
        disable_busy_cursor()
        self.busy = False

    def show_impact(self, report_path):
        """Show the report.

        .. versionadded: 4.0

        :param report_path: The path to the report.
        :type report_path: basestring
        """
        # We can display an impact report.
        # We need to open the file in UTF-8, the HTML may have some accents
        with codecs.open(report_path, 'r', 'utf-8') as report_file:
            report = report_file.read()

        self.print_button.setEnabled(True)
        # right now send the report as html texts, not message
        send_static_message(self, report)
        # also hide the question and show the show question button
        self.show_question_button.setVisible(True)
        self.question_group.setEnabled(True)
        self.question_group.setVisible(False)

    def show_generic_keywords(self, layer):
        """Show the keywords defined for the active layer.

        .. note:: The print button will be disabled if this method is called.

        .. versionchanged:: 3.3 - changed parameter from keywords object
            to a layer object so that we can show extra stuff like CRS and
            data source in the keywords.

        :param layer: A QGIS layer.
        :type layer: QgsMapLayer
        """
        keywords = KeywordIO(layer)
        self.print_button.setEnabled(False)
        message = keywords.to_message()
        send_static_message(self, message)
        self.show_question_button.setVisible(False)
        self.question_group.setEnabled(True)
        self.question_group.setVisible(True)

    @pyqtSlot('QgsMapLayer')
    def layer_changed(self, layer):
        """Handler for when the QGIS active layer is changed.

        If the active layer is changed and it has keywords and a report,
        show the report.

        :param layer: QgsMapLayer instance that is now active
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer

        """
        # Don't handle this event if we are already handling another layer
        # addition or removal event.
        if self.get_layers_lock:
            return

        # Do nothing if there is no active layer - see #1861
        if not self._has_active_layer():
            send_static_message(self, getting_started_message())

        # Now try to read the keywords and show them in the dock
        try:
            keywords = self.keyword_io.read_keywords(layer)

            # list of layer purpose to show impact report
            impacted_layer = [
                layer_purpose_exposure_impacted['key'],
                layer_purpose_aggregate_hazard_impacted['key'],
                layer_purpose_aggregation_impacted['key'],
                layer_purpose_analysis_impacted['key'],
                layer_purpose_exposure_breakdown['key'],
            ]

            show_keywords = True
            if keywords.get('layer_purpose') in impacted_layer:
                report_path = os.path.dirname(layer.source())
                report_path = os.path.join(
                    report_path, 'output/impact-report-output.html')

                if os.path.exists(report_path):
                    show_keywords = False
                    self.show_impact(report_path)

            if show_keywords:
                if inasafe_keyword_version_key not in keywords.keys():
                    show_keyword_version_message(
                        self, 'No Version', self.inasafe_version)
                    self.print_button.setEnabled(False)
                else:
                    keyword_version = str(keywords.get(
                        inasafe_keyword_version_key))
                    supported = is_keyword_version_supported(
                        keyword_version)
                    if supported:
                        self.show_generic_keywords(layer)
                    else:
                        # Layer version is not supported
                        show_keyword_version_message(
                            self, keyword_version, self.inasafe_version)
                    self.print_button.setEnabled(False)

        # TODO: maybe we need to split these apart more to give mode
        # TODO: granular error messages TS
        except (KeywordNotFoundError,
                HashNotFoundError,
                InvalidParameterError,
                NoKeywordsFoundError,
                MetadataReadError,
                AttributeError):
            # Added this check in 3.2 for #1861
            active_layer = self.iface.activeLayer()
            if active_layer is None:
                send_static_message(self, getting_started_message())
            else:
                show_no_keywords_message(self)
                self.print_button.setEnabled(False)
        except Exception as e:  # pylint: disable=broad-except
            error_message = get_error_message(e)
            send_error_message(self, error_message)

    def save_state(self):
        """Save the current state of the ui to an internal class member.

        The saved state can be restored again easily using
        :func:`restore_state`
        """
        state = {
            'hazard': self.hazard_layer_combo.currentText(),
            'exposure': self.exposure_layer_combo.currentText(),
            'aggregation': self.aggregation_layer_combo.currentText(),
            'report': self.results_webview.page().currentFrame().toHtml()}
        self.state = state

    def restore_state(self):
        """Restore the state of the dock to the last known state."""
        if self.state is None:
            return
        for myCount in range(0, self.exposure_layer_combo.count()):
            item_text = self.exposure_layer_combo.itemText(myCount)
            if item_text == self.state['exposure']:
                self.exposure_layer_combo.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.hazard_layer_combo.count()):
            item_text = self.hazard_layer_combo.itemText(myCount)
            if item_text == self.state['hazard']:
                self.hazard_layer_combo.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.aggregation_layer_combo.count()):
            item_text = self.aggregation_layer_combo.itemText(myCount)
            if item_text == self.state['aggregation']:
                self.aggregation_layer_combo.setCurrentIndex(myCount)
                break
        self.results_webview.setHtml(self.state['report'])

    def print_map(self):
        """Open impact report dialog used to tune report when printing."""
        # Check if selected layer is valid
        impact_layer = self.iface.activeLayer()
        if impact_layer is None:
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                self.tr('Please select a valid impact layer before '
                        'trying to print.'))
            return

        # Get output path from datastore
        # Fetch report for pdfs report
        report_path = os.path.dirname(impact_layer.source())
        output_paths = [
            os.path.join(
                report_path,
                'output/impact-report-output.pdf'),
            os.path.join(
                report_path,
                'output/a4-portrait-blue.pdf'),
            os.path.join(
                report_path,
                'output/a4-landscape-blue.pdf'),
        ]

        # Make sure the file paths can wrap nicely:
        wrapped_output_paths = [
            path.replace(os.sep, '<wbr>' + os.sep) for path in
            output_paths]

        # create message to user
        status = m.Message(
            m.Heading(self.tr('Map Creator'), **INFO_STYLE),
            m.Paragraph(self.tr(
                'Your PDF was created....opening using the default PDF '
                'viewer on your system. The generated pdfs were saved '
                'as:')))

        for path in wrapped_output_paths:
            status.add(m.Paragraph(path))

        send_static_message(self, status)

        for path in output_paths:
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path))

    @pyqtSlot('QgsRectangle', 'QgsCoordinateReferenceSystem')
    def define_user_analysis_extent(self, extent, crs):
        """Slot called when user has defined a custom analysis extent.

        .. versionadded: 2.2.0

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: Coordinate reference system for user defined analysis
            extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        extent = QgsGeometry.fromRect(extent)
        self.extent.set_user_extent(extent, crs)
        self.validate_impact_function()

    def _has_active_layer(self):
        """Check if there is a layer active in the legend.

        .. versionadded:: 3.1

        :returns: True if there is a layer hightlighted in the legend.
        :rtype: bool
        """
        layer = self.iface.activeLayer()
        return layer is not None

    def _layer_count(self):
        """Return the count of layers in the legend.

        .. versionadded: 3.1

        :returns: Number of layers in the legend, regardless of their
            visibility status.
        :rtype: int
        """

        legend = self.iface.legendInterface()
        layers = legend.layers()
        count = len(layers)
        return count

    def _visible_layers_count(self):
        """Calculate the number of visible layers in the legend.

        .. versionadded: 3.1

        :returns: Count of layers that are actually visible.
        :rtype: int
        """
        legend = self.iface.legendInterface()
        layers = legend.layers()
        visible_count = 0
        for layer in layers:
            if legend.isLayerVisible(layer):
                visible_count += 1
        return visible_count

    def validate_impact_function(self):
        """Helper method to evaluate the current state of the impact function.

        This function will determine if it is appropriate for the OK button to
        be enabled or not. Only this function is able to change the status of
        the button.

        This function will return a ready to run impact function or None if it
        is not ready.

        This slot is called on pan, zoom, layer visibility changes.

        .. versionadded:: 4.0
        """
        # First, we check if the dock is not busy.
        if self.busy:
            return False, None

        # Then, we need to check if the question area is correct.
        flag, message = self._validate_question_area()
        if not flag:
            send_static_message(self, message)
            self.run_button.setEnabled(False)
            self.extent.clear_next_analysis_extent()
            return False, None

        # Finally, we need to check if an IF can run.
        impact_function = ImpactFunction()
        impact_function.hazard = self.get_hazard_layer()
        impact_function.exposure = self.get_exposure_layer()
        aggregation = self.get_aggregation_layer()

        if aggregation:
            impact_function.aggregation = aggregation
            impact_function.use_selected_features_only = (
                setting('useSelectedFeaturesOnly', False, bool))
        else:
            mode = setting('analysis_extents_mode')
            if self.extent.user_extent:
                # This like a hack to transform a geometry to a rectangle.
                # self.extent.user_extent is a QgsGeometry.
                # impact_function.requested_extent needs a QgsRectangle.
                wkt = self.extent.user_extent.exportToWkt()
                impact_function.requested_extent = wkt_to_rectangle(wkt)
                impact_function.requested_extent_crs = self.extent.crs

            elif mode == HAZARD_EXPOSURE_VIEW:
                impact_function.requested_extent = (
                    self.iface.mapCanvas().extent())
                impact_function.requested_extent_crs = self.extent.crs

        status, message = impact_function.prepare()
        if status == PREPARE_SUCCESS:

            show_confirmations = setting(
                'show_extent_confirmations', True, bool)

            if show_confirmations:
                message = self.tr(
                    'The hazard layer, exposure layer and your '
                    'defined analysis area extents all overlap. Press the '
                    'run button below to continue with the analysis.')

                display_information_message_bar(
                    'InaSAFE',
                    self.tr('Analysis environment ready'),
                    message,
                    self.tr('More info ...'),
                    2)

            self.extent.set_next_analysis_extent(
                impact_function.analysis_extent,
                self.get_exposure_layer().crs())

            self.run_button.setEnabled(True)
            send_static_message(self, ready_message())
            return impact_function

        elif status == PREPARE_FAILED_BAD_LAYER:
            self.extent.clear_next_analysis_extent()
            send_error_message(self, message)
            self.run_button.setEnabled(False)
            return None

        elif status == PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT:
            self.extent.clear_next_analysis_extent()
            show_warnings = setting('show_extent_warnings', True, bool)
            if show_warnings:
                display_warning_message_bar(
                    'InaSAFE',
                    tr('The requested extent is not overlapping your layers.'))
            self.run_button.setEnabled(False)
            return None

        elif status == PREPARE_FAILED_INSUFFICIENT_OVERLAP:
            self.extent.clear_next_analysis_extent()
            show_warnings = setting('show_extent_warnings', True, bool)
            if show_warnings:
                display_warning_message_bar(
                    'InaSAFE',
                    self.tr('No overlapping extents'),
                    no_overlap_message())
            self.run_button.setEnabled(False)
            return None

        elif status == PREPARE_FAILED_BAD_INPUT:
            # The user should fix the message. It should be in orange.
            self.extent.clear_next_analysis_extent()
            send_error_message(self, message)
            self.run_button.setEnabled(False)
            return None

        else:
            # An exception has been raised. It should be in red.
            self.extent.clear_next_analysis_extent()
            send_error_message(self, message)
            self.run_button.setEnabled(False)
            return None

    def _validate_question_area(self):
        """Helper method to evaluate the current state of the dialog.

        This function will determine if it is appropriate for the OK button to
        be enabled or not.

        .. note:: The enabled state of the OK button on the dialog will
           NOT be updated (set True or False) depending on the outcome of
           the UI readiness tests performed - **only** True or False
           will be returned by the function.

        :returns: A two-tuple where the first element is a Boolean reflecting
         the results of the validation tests and the second is a message
         indicating any reason why the validation may have failed.
        :rtype: (Boolean, safe.messaging.Message)

        Example::

            flag,message = self._validate_question_area()
        """
        hazard_index = self.hazard_layer_combo.currentIndex()
        exposure_index = self.exposure_layer_combo.currentIndex()
        if hazard_index == -1 or exposure_index == -1:
            message = getting_started_message()
            return False, message
        else:
            return True, None
