from PyQt6.QtGui import QIcon
from PyQt6.QtDesigner import QPyDesignerCustomWidgetPlugin
from imagecolorpicker.pickablecolorlabel import *

class PickableColorLabelPlugin(QPyDesignerCustomWidgetPlugin):
    WidgetName = "PickableColorLabel"
    DomXml = """<ui language='c++'>
    <widget class='{widgetName}' name='{widgetInstanceName}'/>
</ui>
""".format(
    widgetName=WidgetName,
    widgetInstanceName=WidgetName[0].lower() + WidgetName[1:],
)
    IncludeFile = "imagecolorpicker.pickablecolorlabel"
    ShortDescription = "Pick colors from images."
    WidgetGroup = "Team210 Widgets"

    def __init__(self):
        super().__init__()

        self._initialized = False

    def name(self):
        return PickableColorLabelPlugin.WidgetName

    def icon(self):
        return QIcon()

    def group(self):
        return PickableColorLabelPlugin.WidgetGroup

    def toolTip(self):
        return PickableColorLabelPlugin.ShortDescription

    def whatsThis(self):
        return PickableColorLabelPlugin.ShortDescription

    def includeFile(self):
        return PickableColorLabelPlugin.IncludeFile

    def createWidget(self, parent):
        return PickableColorLabel(parent)

    def domXml(self):
        return PickableColorLabelPlugin.DomXml

    def initialize(self, core):
        if self._initialized:
            return

        self._initialized = True

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._initialized
