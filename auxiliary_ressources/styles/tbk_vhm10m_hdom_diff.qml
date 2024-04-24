<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.4-Prizren" styleCategories="Symbology|Labeling">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" name="name" value=""/>
      <Option name="properties"/>
      <Option type="QString" name="type" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false"/>
    </provider>
    <rasterrenderer band="1" alphaBand="-1" type="singlebandpseudocolor" classificationMax="10" classificationMin="-10" opacity="1" nodataColor="">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader classificationMode="2" maximumValue="10" clip="0" colorRampType="DISCRETE" labelPrecision="0" minimumValue="-10">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" name="color1" value="202,0,32,255"/>
              <Option type="QString" name="color2" value="5,113,176,255"/>
              <Option type="QString" name="direction" value="ccw"/>
              <Option type="QString" name="discrete" value="0"/>
              <Option type="QString" name="rampType" value="gradient"/>
              <Option type="QString" name="spec" value="rgb"/>
              <Option type="QString" name="stops" value="0.25;230,110,97,255;rgb;ccw:0.4;245,192,169,255;rgb;ccw:0.6;247,247,247,255;rgb;ccw:0.75;180,214,230,255;rgb;ccw:1;99,169,207,255;rgb;ccw"/>
            </Option>
          </colorramp>
          <item alpha="255" label="&lt;= -10 m" value="-10" color="#ca0020"/>
          <item alpha="255" label="-10 - -5 m" value="-5" color="#e66e61"/>
          <item alpha="255" label="-5 - -2 m" value="-2" color="#f5c0a9"/>
          <item alpha="255" label="-2 - 2 m" value="2" color="#f7f7f7"/>
          <item alpha="255" label="2 - 5 m" value="5" color="#b4d6e6"/>
          <item alpha="255" label="5 - 10 m" value="10" color="#63a9cf"/>
          <item alpha="255" label="> 10 m" value="inf" color="#0571b0"/>
          <rampLegendSettings direction="0" orientation="2" prefix="" useContinuousLegend="1" minimumLabel="" suffix="" maximumLabel="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="invalid" name="decimal_separator"/>
                <Option type="int" name="decimals" value="6"/>
                <Option type="int" name="rounding_type" value="0"/>
                <Option type="bool" name="show_plus" value="false"/>
                <Option type="bool" name="show_thousand_separator" value="true"/>
                <Option type="bool" name="show_trailing_zeros" value="false"/>
                <Option type="invalid" name="thousand_separator"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" brightness="0" contrast="0"/>
    <huesaturation colorizeStrength="100" colorizeOn="0" saturation="0" invertColors="0" grayscaleMode="0" colorizeBlue="128" colorizeRed="255" colorizeGreen="128"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
