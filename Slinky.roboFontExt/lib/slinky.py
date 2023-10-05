# menuTitle: Slinky
# author: Ryan Bugden

from math import ceil
from fontTools.misc.fixedTools import otRound
import ezui
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.UI import getDefault


EXTENSION_KEY = 'com.ryanbugden.slinky.settings'


class Slinky(ezui.WindowController):

    def build(self):
        content = """
        * TwoColumnForm           @form
        
        > : Units:     
        > [_1000 _]               @unitsTextField
        
        > : Scale From:
        > (X) UPM                 @originRadios
        > ( ) Asc–Desc Height          
        
        > : UPM Options:
        > (X) Scale               @upmOptionsRadios
        > ( ) Match Asc–Desc Height  
        > ( ) Don’t Change
                
        > ---
        
        > : Scale:
        > [X] Anchors             @scaleAnchorsCheckbox
        > [X] Guidelines          @scaleGuidelinesCheckbox
        > [X] Images              @scaleImagesCheckbox
        > [X] Kerning             @scaleKerningCheckbox
        > [X] Component Offset    @translateComponentsCheckbox
       
        > : Round:
        > (X) 1 Unit              @roundRadios
        > ( ) Don’t Round          
        
        > ---
        
        > : Layer(s):
        > ( ) Default Layer       @layersRadios
        > (X) All Layers
        
        > ---
        
        > : Font(s):
        > (X) Current Font        @fontsRadios
        > ( ) All Fonts

        > ---
        
        > : Perform:
        > (X) Directly To Font    @performOptionsRadios
        > ( ) As New Font
        
        -----------------
        """
        footer="""
        !* Save before scaling.   @saveLabel
        %%                        @progressSpinner
        (Scale)                   @scaleButton
        """
        title_width = 100
        item_width = 180
        descriptionData = dict(
            form=dict(
                titleColumnWidth=title_width,
                itemColumnWidth=item_width
            ),
            unitsTextField=dict(
                placeholder=1000,
                valueType="integer",
                valueWidth=50,
                valueIncrement=1,
            ),
            upmTextField=dict(
                placeholder=1000,
                valueType="integer",
                valueWidth=50,
                valueIncrement=1,
            ),
            saveLabel=dict(
                gravity='leading'
            ),
            scaleButton=dict(
                width=item_width,
            )
        )
        self.w = ezui.EZWindow(
            title="Slinky",
            size="auto",
            content=content,
            descriptionData=descriptionData,
            footer=footer,
            controller=self
        )
        self.progressSpinner = self.w.getItem("progressSpinner")
        
        prefs = getExtensionDefault(EXTENSION_KEY, fallback=self.w.getItemValues())
        try: self.w.setItemValues(prefs)
        except KeyError: pass

        self.upm_options = self.w.getItem("upmOptionsRadios")
        self.upm_setting_stored = self.upm_options.get()
        self.originRadiosCallback(self.w.getItem("originRadios"))
        self.performOptionsRadiosCallback(self.w.getItem("performOptionsRadios"))
        
    def started(self):
        # Position the window where it was last
        _, _, ww, wh =  self.w.getPosSize()
        pos_size = getExtensionDefault(EXTENSION_KEY + ".windowPosSize", fallback=(200, 200, ww, wh))
        self.w.setPosSize(pos_size)

        self.w.open()
        self.progressSpinner.show(False)

    def destroy(self):
        setExtensionDefault(EXTENSION_KEY, self.w.getItemValues())
        setExtensionDefault(EXTENSION_KEY + ".windowPosSize", self.w.getPosSize())
        # self.w.close()
        
    def round_list(self, l):
        new_list = []
        for item in l:
            if self.round_stuff == 0:
                item = otRound(item)
            new_list.append(item)
        return new_list
        
    def originRadiosCallback(self, sender):
        value = sender.get()
        if value == 0:
            self.upm_setting_stored = self.upm_options.get()
            self.upm_options.set(0)
            self.upm_options.enable(False)
        elif value == 1:
            self.upm_options.set(self.upm_setting_stored)
            self.upm_options.enable(True)
            
    def performOptionsRadiosCallback(self, sender):
        value = sender.get()
        if value == 0:
            self.w.getItem("saveLabel").show(True)
        elif value == 1:
            self.w.getItem("saveLabel").show(False)
        
    progressSpinnerAnimating = False
    def scaleButtonCallback(self, sender):
        self.progressSpinner.show(True)
        self.progressSpinnerAnimating = True
        self.progressSpinner.start()
        
        origin_choice       = self.w.getItem("originRadios").get()
        self.round_stuff    = self.w.getItem('roundRadios').get()
        desired_height      = self.w.getItem('unitsTextField').get()
        upm_treatment       = self.upm_options.get()
        
        scale_guidelines    = self.w.getItem('scaleGuidelinesCheckbox').get()
        scale_anchors       = self.w.getItem('scaleAnchorsCheckbox').get()
        scale_images        = self.w.getItem('scaleImagesCheckbox').get()
        scale_kerning       = self.w.getItem('scaleKerningCheckbox').get()
        trans_components    = self.w.getItem('translateComponentsCheckbox').get()
        
        all_fonts_choice    = self.w.getItem('fontsRadios').get()
        all_layers_choice   = self.w.getItem('layersRadios').get()
        perform_choice      = self.w.getItem('performOptionsRadios').get()

        fonts = AllFonts()
        if all_fonts_choice == 0:
            fonts = [fonts[0]]
            
        for font in fonts:
            
            # Whether or not the operation will take place on the font or generated as a new font.
            f = font
            if perform_choice == 1:
                f = font.copy()

            # Which layers will be scaled            
            layers = f.layers
            if all_layers_choice == 0:
                layers = [f.defaultLayer]
            
            # Scale UPM and figure out the basis for the scale factor overall
            old_upm = f.info.unitsPerEm
            old_asc_desc = f.info.ascender - f.info.descender
            # Scale from UPM
            if origin_choice == 0:
                height = old_upm
                factor = desired_height / height
                f.info.unitsPerEm = otRound(desired_height)
            # Scale from asc-desc
            else:
                height = old_asc_desc
                factor = desired_height / height
                if upm_treatment == 0:
                    f.info.unitsPerEm = otRound(old_upm * factor)
                elif upm_treatment == 1:
                    f.info.unitsPerEm = otRound(desired_height)
                
            # Scale each value in these blue-value lists
            for attr in ["descender", "xHeight", "capHeight", "ascender", "openTypeHeadLowestRecPPEM", "openTypeHheaAscender", "openTypeHheaDescender", "openTypeHheaLineGap", "openTypeHheaCaretSlopeRise", "openTypeHheaCaretSlopeRun", "openTypeHheaCaretOffset", "openTypeOS2WeightClass", "openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap", "openTypeOS2WinAscent", "openTypeOS2WinDescent", "openTypeOS2SubscriptXSize", "openTypeOS2SubscriptYSize", "openTypeOS2SubscriptXOffset", "openTypeOS2SubscriptYOffset", "openTypeOS2SuperscriptXSize", "openTypeOS2SuperscriptYSize", "openTypeOS2SuperscriptXOffset", "openTypeOS2SuperscriptYOffset", "openTypeOS2StrikeoutSize", "openTypeOS2StrikeoutPosition", "openTypeVheaVertTypoAscender", "openTypeVheaVertTypoDescender", "openTypeVheaVertTypoLineGap", "openTypeVheaCaretSlopeRise", "openTypeVheaCaretSlopeRun", "openTypeVheaCaretOffset", "postscriptSlantAngle", "postscriptUnderlineThickness", "postscriptUnderlinePosition", "postscriptBlueValues", "postscriptOtherBlues", "postscriptFamilyBlues", "postscriptFamilyOtherBlues", "postscriptStemSnapH", "postscriptStemSnapV", "postscriptBlueFuzz", "postscriptBlueShift", "postscriptDefaultWidthX", "postscriptNominalWidthX"]:
                value = getattr(f.info, attr)
                if value == None or value == []:
                    continue
                if type(value).__name__ == "list":
                    new_value = [otRound(item * factor) for item in value]
                else:
                    new_value = round(otRound(value * factor))
                try:
                    setattr(f.info, attr, new_value)
                except ValueError:
                    print(f"Slinky Error: There was an issue setting the {attr} to value: {new_value}")
                    
            # Scale font guidelines
            if scale_guidelines == True:
                for guideline in f.guidelines:
                    guideline.scaleBy(factor, (0,0))
                    guideline.x, guideline.y = self.round_list([guideline.x, guideline.y])
             
            # Scale kerning
            if scale_kerning == True:
                f.kerning.scaleBy(factor)
            
            # Scale things in every glyph in every chosen layer
            for layer in layers:
                for g in layer:
                    with g.undo('Scale glyph (using Slinky)'):

                        # Scale glyph drawings
                        for c in g.contours:
                            c.scaleBy(factor, (0,0))
                            if self.round_stuff != 1:
                                for pt in c.points:
                                    pt.x, pt.y = self.round_list([pt.x, pt.y])
                            
                        # Scale anchors
                        if scale_anchors == True:
                            for a in g.anchors:
                                a.scaleBy(factor, (0,0))
                                if self.round_stuff != 1:
                                    a.x, a.y = self.round_list([a.x, a.y])
                    
                        # Scale component offset
                        if trans_components == True:
                            for comp in g.components:
                                x, y = comp.offset
                                x *= factor
                                y *= factor
                                if self.round_stuff != 1:
                                    x, y = self.round_list([x, y])
                                comp.offset = x, y
                            
                        # Scale glyph guidelines
                        if scale_guidelines == True:
                            for guideline in g.guidelines:
                                guideline.scaleBy(factor, (0,0))
                                if self.round_stuff != 1:
                                    guideline.x, guideline.y = self.round_list([guideline.x, guideline.y])
                                                
                        # Scale images                
                        if scale_images == True:
                            g.image.scaleBy(factor, (0,0))
                            if self.round_stuff != 1:
                                x, y = g.image.offset
                                g.image.offset = self.round_list([x, y])
                        
                        g.width *= factor
                        
            # Finish up
            f.changed()

            # Open the new font
            if perform_choice == 1:
                f.openInterface()
            
            # Print a report
            print(f"\n|/|/|/|/|/|/||/|/|/|/|/|/|/|/|/||/|/|/|")
            print(f"Slinky Report - {f.info.familyName} {f.info.styleName}:")
            if perform_choice == 1:
                print(f"\tMade and opened a copy")
            print(f"\tScaled by a factor of {factor}")
            if f.info.ascender - f.info.descender != old_asc_desc:
                print(f"\tChanged ascender-to-descender height: {old_asc_desc} → {f.info.ascender - f.info.descender}")
            else:
                print(f"\tDid not change ascender-to-descender height")
            if f.info.unitsPerEm != old_upm:
                print(f"\tChanged UPM: {old_upm} → {f.info.unitsPerEm}")
            else:
                print(f"\tDid not change UPM")
            
        self.progressSpinner.stop()
        self.progressSpinnerAnimating = False
        self.progressSpinner.show(False)


Slinky()