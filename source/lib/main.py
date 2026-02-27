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
        
        > : Scale Using:
        > (X) UPM                 @basisRadios
        > ( ) Asc–Desc Height  
        > ( ) Cap-Height                  
        > ( ) Percentage          
        
        > : Value:   
        > * HorizontalStack  
        >> [_1000 _]              @valueTextField
        >> units                  @valueLabel
        
        > ---
        
        > : Scale:
        > [ ] UPM                 @scaleUPMCheckbox
        > [X] Anchors             @scaleAnchorsCheckbox
        > [X] Guidelines          @scaleGuidelinesCheckbox
        > [X] Images              @scaleImagesCheckbox
        > [X] Kerning             @scaleKerningCheckbox
        > [X] Component Offset    @scaleCompOffsetCheckbox
        > [X] Italic Slant Offset @scaleSlantOffsetCheckbox
       
        > : Round:
        > ( ) Don’t Round         @roundRadios
        > (X) 1 Unit 
        
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
            valueTextField=dict(
                placeholder=1000,
                valueType="float",
                valueWidth=50,
                width=50,
                valueIncrement=1,
                minValue=0.01
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
        try: 
            self.w.setItemValues(prefs)
        except KeyError: 
            pass
        self.basisRadiosCallback(self.w.getItem("basisRadios"))
        self.performOptionsRadiosCallback(self.w.getItem("performOptionsRadios"))
        
    def started(self):
        self.w.open()
        self.progressSpinner.show(False)

    def destroy(self):
        setExtensionDefault(EXTENSION_KEY, self.w.getItemValues())
        
    def basisRadiosCallback(self, sender):
        '''
        Keeps an eye on the Scale Using options and 
        updates elements of the UI appropriately.
        '''
        basis = sender.get()
        value_label = self.w.getItem("valueLabel")
        # Percentage
        if basis == 3:
            value_label.set("%")
        else:
            value_label.set("units")
        # UPM
        if basis == 0:
            self.w.getItem("scaleUPMCheckbox").enable(False)
        else:
            self.w.getItem("scaleUPMCheckbox").enable(True)
            
    def performOptionsRadiosCallback(self, sender):
        '''
        Keeps an eye on the Perform options and warns 
        the user, if about to scale the fonts directly, 
        to save the fonts beforehand.
        '''
        value = sender.get()
        if value == 0:
            self.w.getItem("saveLabel").show(True)
        elif value == 1:
            self.w.getItem("saveLabel").show(False)
            
    def start_spinner(self):
        # Move save label away
        self.w.getItem("saveLabel").show(False)
        self.progressSpinner.show(True)
        self.progressSpinnerAnimating = True
        self.progressSpinner.start()
        
    def stop_spinner(self):
        self.progressSpinner.stop()
        self.progressSpinnerAnimating = False
        self.progressSpinner.show(False)
        # Bring back save label if needed
        self.performOptionsRadiosCallback(self.w.getItem("performOptionsRadios"))
        
    progressSpinnerAnimating = False
    def scaleButtonCallback(self, sender):
        '''Scales the font(s).'''
        self.start_spinner()
        
        basis_choice        = self.w.getItem("basisRadios").get()
        round_stuff         = self.w.getItem('roundRadios').get()
        desired_value       = self.w.getItem('valueTextField').get()
        
        scale_UPM           = self.w.getItem('scaleUPMCheckbox').get()
        scale_guidelines    = self.w.getItem('scaleGuidelinesCheckbox').get()
        scale_anchors       = self.w.getItem('scaleAnchorsCheckbox').get()
        scale_images        = self.w.getItem('scaleImagesCheckbox').get()
        scale_kerning       = self.w.getItem('scaleKerningCheckbox').get()
        scale_comp_offset   = self.w.getItem('scaleCompOffsetCheckbox').get()
        scale_ital_offset   = self.w.getItem('scaleSlantOffsetCheckbox').get()
        
        all_fonts_choice    = self.w.getItem('fontsRadios').get()
        all_layers_choice   = self.w.getItem('layersRadios').get()
        perform_choice      = self.w.getItem('performOptionsRadios').get()

        fonts = AllFonts()
        if not fonts:
            print(f"Slinky: Open a font first.")
            self.stop_spinner()
            return
        if all_fonts_choice == 0:
            fonts = [fonts[0]]
            
        for font in fonts:
            
            # Whether or not the operation will take place on the font or generated as a new font.
            f = font
            if perform_choice == 1:
                f = font.copy()
            
            # Grab old value and figure out scale factor overall
            basis_options = [f.info.unitsPerEm, f.info.ascender - f.info.descender, f.info.capHeight, 100]
            current_value = basis_options[basis_choice]
            if current_value == 0:
                print(f"Slinky Error: Avoiding dividing by zero. Change the settings and try again.")
                return
            factor = desired_value / current_value
            
            # Scale UPM
            if scale_UPM == True or basis_choice == 0:
                f.info.unitsPerEm = otRound(basis_options[0] * factor)

            # Scale each value in this list of font info attributes
            values_to_scale = [
                "descender", 
                "xHeight", 
                "capHeight",
                "ascender",
                "openTypeHheaAscender",
                "openTypeHheaDescender",
                "openTypeHheaLineGap",
                "openTypeHheaCaretOffset",
                "openTypeOS2TypoAscender",
                "openTypeOS2TypoDescender",
                "openTypeOS2TypoLineGap",
                "openTypeOS2WinAscent",
                "openTypeOS2WinDescent",
                "openTypeOS2SubscriptXSize",
                "openTypeOS2SubscriptYSize",
                "openTypeOS2SubscriptXOffset",
                "openTypeOS2SubscriptYOffset",
                "openTypeOS2SuperscriptXSize",
                "openTypeOS2SuperscriptYSize",
                "openTypeOS2SuperscriptXOffset",
                "openTypeOS2SuperscriptYOffset",
                "openTypeOS2StrikeoutSize",
                "openTypeOS2StrikeoutPosition",
                "openTypeVheaVertTypoAscender",
                "openTypeVheaVertTypoDescender",
                "openTypeVheaVertTypoLineGap",
                "openTypeVheaCaretOffset",
                "postscriptUnderlineThickness",
                "postscriptUnderlinePosition",
                "postscriptBlueValues",
                "postscriptOtherBlues",
                "postscriptFamilyBlues",
                "postscriptFamilyOtherBlues",
                "postscriptStemSnapH",
                "postscriptStemSnapV",
                "postscriptBlueFuzz",
                "postscriptBlueShift",
                "postscriptDefaultWidthX",
                "postscriptNominalWidthX"
            ]

            for attr in values_to_scale:
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
                    if round_stuff:
                        guideline.round()
             
            # Scale kerning
            if scale_kerning == True:
                f.kerning.scaleBy(factor)

            # Scale italic slant offset
            if scale_ital_offset == True:
                offset_key = 'com.typemytype.robofont.italicSlantOffset'
                if offset_key in f.lib.keys():
                    f.lib[offset_key] = otRound(f.lib[offset_key] * factor)

            # Scale things in every glyph in every chosen layer
            layers = [f.defaultLayer] if all_layers_choice == 0 else f.layers
            for layer in layers:
                for g in layer:
                    with g.undo('Scale Glyph (using Slinky)'):

                        # Scale glyph drawings
                        for c in g.contours:
                            c.scaleBy(factor, (0,0))
                            
                        # Scale anchors
                        if scale_anchors == True:
                            for a in g.anchors:
                                a.scaleBy(factor, (0,0))
                    
                        # Scale component offset
                        if scale_comp_offset == True:
                            for comp in g.components:
                                x, y = comp.offset
                                x *= factor
                                y *= factor
                                comp.offset = x, y
                            
                        # Scale glyph guidelines
                        if scale_guidelines == True:
                            for guideline in g.guidelines:
                                guideline.scaleBy(factor, (0,0))
                                                
                        # Scale images                
                        if scale_images == True:
                            g.image.scaleBy(factor, (0,0))
                        
                        # Scale glyph width
                        g.width *= factor
                        
                        # Round
                        if round_stuff:
                            try:
                                g.round()
                            except NameError:
                                print("Slinky error with rounding. Please update FontParts.")
                        
            # Finish up
            f.changed()

            # Open the new font
            if perform_choice == 1:
                f.openInterface()
            
            # Print a report
            print(f"\n|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|/|")
            print(f"Slinky Report - {f.info.familyName} {f.info.styleName}:")
            if perform_choice == 1:
                print(f"\tMade and opened a copy")
            print(f"\tScaled by a factor of {factor}")
            if f.info.unitsPerEm != basis_options[0]:
                print(f"\tChanged UPM: {basis_options[0]} → {f.info.unitsPerEm}")
            else:
                print(f"\tDid not change UPM")
            if f.info.ascender - f.info.descender != basis_options[1]:
                print(f"\tChanged ascender-to-descender height: {basis_options[1]} → {f.info.ascender - f.info.descender}")
            else:
                print(f"\tDid not change ascender-to-descender height")
            if f.info.capHeight != basis_options[2]:
                print(f"\tChanged cap-height: {basis_options[2]} → {f.info.capHeight}")
            else:
                print(f"\tDid not change cap-height")
            
        self.stop_spinner()


Slinky()
