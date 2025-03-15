from PyQt6.QtGui import QIcon
from PyQt6.QtDesigner import QPyDesignerCustomWidgetPlugin
from imagecolorpicker.gradientpreview import *

class GradientPreviewPlugin(QPyDesignerCustomWidgetPlugin):
    WidgetName = "GradientPreview"
    DomXml = """<ui language='c++'>
    <widget class='{widgetName}' name='{widgetInstanceName}'/>
</ui>
""".format(
    widgetName=WidgetName,
    widgetInstanceName=WidgetName[0].lower() + WidgetName[1:],
)
    IncludeFile = "imagecolorpicker.gradientpreview"
    ShortDescription = "Preview a gradient."
    WidgetGroup = "Team210 Widgets"

    def __init__(self):
        super().__init__()

        self._initialized = False

    def name(self):
        return GradientPreviewPlugin.WidgetName

    def icon(self):
        return QIcon()

    def group(self):
        return GradientPreviewPlugin.WidgetGroup

    def toolTip(self):
        return GradientPreviewPlugin.ShortDescription

    def whatsThis(self):
        return GradientPreviewPlugin.ShortDescription

    def includeFile(self):
        return GradientPreviewPlugin.IncludeFile

    def createWidget(self, parent):
        return GradientPreview(parent)

    def domXml(self):
        return GradientPreviewPlugin.DomXml

    def initialize(self, core):
        if self._initialized:
            return

        self._initialized = True

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._initialized
