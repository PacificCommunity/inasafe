# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options_dialog_base.ui'
#
# Created: Thu Jan 23 14:55:00 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_OptionsDialogBase(object):
    def setupUi(self, OptionsDialogBase):
        OptionsDialogBase.setObjectName(_fromUtf8("OptionsDialogBase"))
        OptionsDialogBase.resize(596, 387)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        OptionsDialogBase.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(OptionsDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(OptionsDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.scrollArea = QtGui.QScrollArea(OptionsDialogBase)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -327, 563, 1049))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.grpNotImplemented = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.grpNotImplemented.setObjectName(_fromUtf8("grpNotImplemented"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grpNotImplemented)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.cbxBubbleLayersUp = QtGui.QCheckBox(self.grpNotImplemented)
        self.cbxBubbleLayersUp.setEnabled(True)
        self.cbxBubbleLayersUp.setObjectName(_fromUtf8("cbxBubbleLayersUp"))
        self.gridLayout_3.addWidget(self.cbxBubbleLayersUp, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.grpNotImplemented)
        self.label.setEnabled(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEdit = QtGui.QLineEdit(self.grpNotImplemented)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.toolButton = QtGui.QToolButton(self.grpNotImplemented)
        self.toolButton.setEnabled(True)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout_2.addWidget(self.toolButton)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.grpNotImplemented)
        self.label_4.setEnabled(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 7, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lineEdit_4 = QtGui.QLineEdit(self.grpNotImplemented)
        self.lineEdit_4.setEnabled(True)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.horizontalLayout_4.addWidget(self.lineEdit_4)
        self.toolButton_4 = QtGui.QToolButton(self.grpNotImplemented)
        self.toolButton_4.setEnabled(True)
        self.toolButton_4.setObjectName(_fromUtf8("toolButton_4"))
        self.horizontalLayout_4.addWidget(self.toolButton_4)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 8, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_5 = QtGui.QLabel(self.grpNotImplemented)
        self.label_5.setEnabled(True)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_5.addWidget(self.label_5)
        self.spinBox = QtGui.QSpinBox(self.grpNotImplemented)
        self.spinBox.setEnabled(True)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.horizontalLayout_5.addWidget(self.spinBox)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 9, 0, 1, 1)
        self.gridLayout_2.addWidget(self.grpNotImplemented, 21, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 24, 0, 1, 1)
        self.cbxUseSentry = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxUseSentry.setObjectName(_fromUtf8("cbxUseSentry"))
        self.gridLayout_2.addWidget(self.cbxUseSentry, 7, 0, 1, 1)
        self.textBrowser = QtGui.QTextBrowser(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout_2.addWidget(self.textBrowser, 8, 0, 1, 1)
        self.cbxNativeZonalStats = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxNativeZonalStats.setObjectName(_fromUtf8("cbxNativeZonalStats"))
        self.gridLayout_2.addWidget(self.cbxNativeZonalStats, 6, 0, 1, 1)
        self.cbxClipToViewport = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxClipToViewport.setChecked(False)
        self.cbxClipToViewport.setObjectName(_fromUtf8("cbxClipToViewport"))
        self.gridLayout_2.addWidget(self.cbxClipToViewport, 4, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.leOrgLogoPath = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.leOrgLogoPath.setEnabled(True)
        self.leOrgLogoPath.setObjectName(_fromUtf8("leOrgLogoPath"))
        self.horizontalLayout_3.addWidget(self.leOrgLogoPath)
        self.toolOrgLogoPath = QtGui.QToolButton(self.scrollAreaWidgetContents)
        self.toolOrgLogoPath.setEnabled(True)
        self.toolOrgLogoPath.setObjectName(_fromUtf8("toolOrgLogoPath"))
        self.horizontalLayout_3.addWidget(self.toolOrgLogoPath)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 16, 0, 1, 1)
        self.lblKeywordCache = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblKeywordCache.setEnabled(True)
        self.lblKeywordCache.setObjectName(_fromUtf8("lblKeywordCache"))
        self.gridLayout_2.addWidget(self.lblKeywordCache, 12, 0, 1, 1)
        self.cbxZoomToImpact = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxZoomToImpact.setEnabled(True)
        self.cbxZoomToImpact.setObjectName(_fromUtf8("cbxZoomToImpact"))
        self.gridLayout_2.addWidget(self.cbxZoomToImpact, 2, 0, 1, 1)
        self.cbxHideExposure = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxHideExposure.setEnabled(True)
        self.cbxHideExposure.setObjectName(_fromUtf8("cbxHideExposure"))
        self.gridLayout_2.addWidget(self.cbxHideExposure, 3, 0, 1, 1)
        self.cbxUseThread = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxUseThread.setObjectName(_fromUtf8("cbxUseThread"))
        self.gridLayout_2.addWidget(self.cbxUseThread, 23, 0, 1, 1)
        self.cbxSetLayerNameFromTitle = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxSetLayerNameFromTitle.setEnabled(True)
        self.cbxSetLayerNameFromTitle.setObjectName(_fromUtf8("cbxSetLayerNameFromTitle"))
        self.gridLayout_2.addWidget(self.cbxSetLayerNameFromTitle, 1, 0, 1, 1)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_6 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_7.addWidget(self.label_6)
        self.dsbFemaleRatioDefault = QtGui.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.dsbFemaleRatioDefault.setAccelerated(True)
        self.dsbFemaleRatioDefault.setMaximum(1.0)
        self.dsbFemaleRatioDefault.setSingleStep(0.01)
        self.dsbFemaleRatioDefault.setObjectName(_fromUtf8("dsbFemaleRatioDefault"))
        self.horizontalLayout_7.addWidget(self.dsbFemaleRatioDefault)
        self.gridLayout_2.addLayout(self.horizontalLayout_7, 11, 0, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.leKeywordCachePath = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.leKeywordCachePath.setEnabled(True)
        self.leKeywordCachePath.setObjectName(_fromUtf8("leKeywordCachePath"))
        self.horizontalLayout_6.addWidget(self.leKeywordCachePath)
        self.toolKeywordCachePath = QtGui.QToolButton(self.scrollAreaWidgetContents)
        self.toolKeywordCachePath.setEnabled(True)
        self.toolKeywordCachePath.setObjectName(_fromUtf8("toolKeywordCachePath"))
        self.horizontalLayout_6.addWidget(self.toolKeywordCachePath)
        self.gridLayout_2.addLayout(self.horizontalLayout_6, 14, 0, 1, 1)
        self.cbxDevMode = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxDevMode.setObjectName(_fromUtf8("cbxDevMode"))
        self.gridLayout_2.addWidget(self.cbxDevMode, 22, 0, 1, 1)
        self.cbxVisibleLayersOnly = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxVisibleLayersOnly.setObjectName(_fromUtf8("cbxVisibleLayersOnly"))
        self.gridLayout_2.addWidget(self.cbxVisibleLayersOnly, 0, 0, 1, 1)
        self.cbxClipHard = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxClipHard.setObjectName(_fromUtf8("cbxClipHard"))
        self.gridLayout_2.addWidget(self.cbxClipHard, 5, 0, 1, 1)
        self.cbxShowPostprocessingLayers = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.cbxShowPostprocessingLayers.setObjectName(_fromUtf8("cbxShowPostprocessingLayers"))
        self.gridLayout_2.addWidget(self.cbxShowPostprocessingLayers, 9, 0, 1, 1)
        self.lblOrganisationLogo = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblOrganisationLogo.setEnabled(True)
        self.lblOrganisationLogo.setObjectName(_fromUtf8("lblOrganisationLogo"))
        self.gridLayout_2.addWidget(self.lblOrganisationLogo, 15, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leReportTemplatePath = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.leReportTemplatePath.setEnabled(True)
        self.leReportTemplatePath.setObjectName(_fromUtf8("leReportTemplatePath"))
        self.horizontalLayout.addWidget(self.leReportTemplatePath)
        self.toolReportTemplatePath = QtGui.QToolButton(self.scrollAreaWidgetContents)
        self.toolReportTemplatePath.setEnabled(True)
        self.toolReportTemplatePath.setObjectName(_fromUtf8("toolReportTemplatePath"))
        self.horizontalLayout.addWidget(self.toolReportTemplatePath)
        self.gridLayout_2.addLayout(self.horizontalLayout, 18, 0, 1, 1)
        self.lblReportTemplate = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblReportTemplate.setEnabled(True)
        self.lblReportTemplate.setObjectName(_fromUtf8("lblReportTemplate"))
        self.gridLayout_2.addWidget(self.lblReportTemplate, 17, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 19, 0, 1, 1)
        self.txtDisclaimer = QtGui.QPlainTextEdit(self.scrollAreaWidgetContents)
        self.txtDisclaimer.setObjectName(_fromUtf8("txtDisclaimer"))
        self.gridLayout_2.addWidget(self.txtDisclaimer, 20, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)

        self.retranslateUi(OptionsDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OptionsDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OptionsDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(OptionsDialogBase)
        OptionsDialogBase.setTabOrder(self.cbxVisibleLayersOnly, self.cbxSetLayerNameFromTitle)
        OptionsDialogBase.setTabOrder(self.cbxSetLayerNameFromTitle, self.lineEdit)
        OptionsDialogBase.setTabOrder(self.lineEdit, self.toolButton)
        OptionsDialogBase.setTabOrder(self.toolButton, self.leReportTemplatePath)
        OptionsDialogBase.setTabOrder(self.leReportTemplatePath, self.toolReportTemplatePath)
        OptionsDialogBase.setTabOrder(self.toolReportTemplatePath, self.leOrgLogoPath)
        OptionsDialogBase.setTabOrder(self.leOrgLogoPath, self.toolOrgLogoPath)
        OptionsDialogBase.setTabOrder(self.toolOrgLogoPath, self.lineEdit_4)
        OptionsDialogBase.setTabOrder(self.lineEdit_4, self.toolButton_4)
        OptionsDialogBase.setTabOrder(self.toolButton_4, self.spinBox)
        OptionsDialogBase.setTabOrder(self.spinBox, self.cbxUseThread)
        OptionsDialogBase.setTabOrder(self.cbxUseThread, self.buttonBox)
        OptionsDialogBase.setTabOrder(self.buttonBox, self.scrollArea)

    def retranslateUi(self, OptionsDialogBase):
        OptionsDialogBase.setWindowTitle(_translate("OptionsDialogBase", "InaSAFE - Options", None))
        self.grpNotImplemented.setTitle(_translate("OptionsDialogBase", "Not yet implemented", None))
        self.cbxBubbleLayersUp.setText(_translate("OptionsDialogBase", "Bubble exposure and hazard layers to top when selected", None))
        self.label.setText(_translate("OptionsDialogBase", "Location for results", None))
        self.toolButton.setText(_translate("OptionsDialogBase", "...", None))
        self.label_4.setText(_translate("OptionsDialogBase", "Organisation name (for maps, reports etc.)", None))
        self.toolButton_4.setText(_translate("OptionsDialogBase", "...", None))
        self.label_5.setText(_translate("OptionsDialogBase", "DPI (Maps and reports)", None))
        self.cbxUseSentry.setText(_translate("OptionsDialogBase", "Help to improve InaSAFE by submitting errors to a remote server", None))
        self.textBrowser.setHtml(_translate("OptionsDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#f50000;\">Note:</span> The above setting requires a QGIS restart to disable / enable. Error messages and diagnostic information will be posted to http://sentry.linfiniti.com/inasafe-desktop/. Some institutions may not allow you to enable this feature - check with your network administrator if unsure. Although the data is submitted anonymously, the information contained in tracebacks may contain file system paths which reveal your identity or other information from your system.</p></body></html>", None))
        self.cbxNativeZonalStats.setText(_translate("OptionsDialogBase", "Use QGIS zonal statistics (not recommended for QGIS 1.8)", None))
        self.cbxClipToViewport.setToolTip(_translate("OptionsDialogBase", "Turn on to clip hazard and exposure layers to the currently  visible extent on the map canvas", None))
        self.cbxClipToViewport.setText(_translate("OptionsDialogBase", "Clip datasets to visible extent before analysis", None))
        self.toolOrgLogoPath.setText(_translate("OptionsDialogBase", "...", None))
        self.lblKeywordCache.setText(_translate("OptionsDialogBase", "Keyword cache for remote datasources", None))
        self.cbxZoomToImpact.setText(_translate("OptionsDialogBase", "Zoom to impact layer on scenario estimate completion", None))
        self.cbxHideExposure.setText(_translate("OptionsDialogBase", "Hide exposure layer on scenario estimate completion", None))
        self.cbxUseThread.setText(_translate("OptionsDialogBase", "Run analysis in a separate thread (experimental)", None))
        self.cbxSetLayerNameFromTitle.setText(_translate("OptionsDialogBase", "Set QGIS layer name from \'title\' in keywords", None))
        self.label_6.setText(_translate("OptionsDialogBase", "Female ratio default value", None))
        self.toolKeywordCachePath.setText(_translate("OptionsDialogBase", "...", None))
        self.cbxDevMode.setText(_translate("OptionsDialogBase", "Enable developer mode (needs restart)", None))
        self.cbxVisibleLayersOnly.setText(_translate("OptionsDialogBase", "Only show visible layers in InaSAFE dock", None))
        self.cbxClipHard.setText(_translate("OptionsDialogBase", "When clipping, also clip features (i.e. will clip polygon smaller)", None))
        self.cbxShowPostprocessingLayers.setToolTip(_translate("OptionsDialogBase", "Turn on to see the intermediate files generated by the postprocessing steps in the map canvas", None))
        self.cbxShowPostprocessingLayers.setText(_translate("OptionsDialogBase", "Show intermediate layers generated by postprocessing", None))
        self.lblOrganisationLogo.setText(_translate("OptionsDialogBase", "Organisation logo", None))
        self.toolReportTemplatePath.setText(_translate("OptionsDialogBase", "...", None))
        self.lblReportTemplate.setText(_translate("OptionsDialogBase", "Report templates directory", None))
        self.label_2.setText(_translate("OptionsDialogBase", "Disclaimer text", None))

import resources_rc
