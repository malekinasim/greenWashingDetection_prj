class GreenwashingDetector:
    def __init__(self,rgb_detector,green_coeff=0.5, blue_coeff=0.05, red_coeff=0.05, 
                        green_brightness_coeff=0.2, green_contrast_coeff=0.2):
        self.rgb_detector = rgb_detector
        self.green_coeff = green_coeff
        self.blue_coeff = blue_coeff  
        self.red_coeff = red_coeff
        self.green_brightness_coeff = green_brightness_coeff
        self.green_contrast_coeff = green_contrast_coeff
        result= self._detect_greenwashing()
        self.greenWashing_score=result[0]
        self.greenWashing_result=result[1]
        
 
    def _detect_greenwashing(self ):
        greenwashing_score = round( self.rgb_detector.green_percentage * self.green_coeff + 
                             self.rgb_detector.blue_percentage * self.blue_coeff + 
                             self.rgb_detector.red_percentage * self.red_coeff + 
                             self.rgb_detector.green_brightness * self.green_brightness_coeff +
                             self.rgb_detector.green_contrast * self.green_contrast_coeff,2)
     
        return  greenwashing_score, "Greenwashing"  if greenwashing_score>50 else "Not Greenwashing"

