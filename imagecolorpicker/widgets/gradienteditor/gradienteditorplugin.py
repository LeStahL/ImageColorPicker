from PyQt6.QtGui import QIcon
from PyQt6.QtDesigner import QPyDesignerCustomWidgetPlugin
from imagecolorpicker.gradienteditor import *

class GradientEditorPlugin(QPyDesignerCustomWidgetPlugin):
    WidgetName = "GradientEditor"
    DomXml = """<ui language='c++'>
    <widget class='{widgetName}' name='{widgetInstanceName}'/>
</ui>
""".format(
    widgetName=WidgetName,
    widgetInstanceName=WidgetName[0].lower() + WidgetName[1:],
)
    IncludeFile = "imagecolorpicker.gradienteditor"
    ShortDescription = "Edit a gradient and pack it."
    WidgetGroup = "Team210 Widgets"

    def __init__(self):
        super().__init__()

        self._initialized = False

    def name(self):
        return GradientEditorPlugin.WidgetName

    def icon(self):
        return QIcon()

    def group(self):
        return GradientEditorPlugin.WidgetGroup

    def toolTip(self):
        return GradientEditorPlugin.ShortDescription

    def whatsThis(self):
        return GradientEditorPlugin.ShortDescription

    def includeFile(self):
        return GradientEditorPlugin.IncludeFile

    def createWidget(self, parent):
        return GradientEditor(parent)

    def domXml(self):
        return GradientEditorPlugin.DomXml

    def initialize(self, core):
        if self._initialized:
            return

        self._initialized = True

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._initialized
