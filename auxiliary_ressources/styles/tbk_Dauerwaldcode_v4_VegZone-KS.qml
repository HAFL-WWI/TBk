<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling" labelsEnabled="1" version="3.34.6-Prizren">
  <renderer-v2 type="categorizedSymbol" enableorderby="0" referencescale="-1" forceraster="0" symbollevels="0" attr="if(&quot;VegZone_Code&quot; IN (-1, 0, 1, 2, 4, 5), &#xd;&#xa;    if(&quot;NH&quot;>50,&#xd;&#xa;        if(&quot;hdom&quot;>=26, &#xd;&#xa;            if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                4,&#xd;&#xa;                    if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                        if(&quot;DG_us&quot; >=20,&#xd;&#xa;                            3,&#xd;&#xa;                            2&#xd;&#xa;                        ),&#xd;&#xa;                        if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                2,&#xd;&#xa;                                1&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                1,&#xd;&#xa;                                0&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                5&#xd;&#xa;            ), &#xd;&#xa;            if(&quot;hdom&quot;>18,&#xd;&#xa;                -1, &#xd;&#xa;                if(&quot;hdom&quot;>10,&#xd;&#xa;                    -2,&#xd;&#xa;                    -3&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        ),&#xd;&#xa;        if(&quot;hdom&quot;>=23, &#xd;&#xa;            if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                    4,&#xd;&#xa;                    if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                        if(&quot;DG_us&quot; >=20,&#xd;&#xa;                            3,&#xd;&#xa;                            2&#xd;&#xa;                        ),&#xd;&#xa;                        if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                2,&#xd;&#xa;                                1&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                1,&#xd;&#xa;                                0&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;            5), &#xd;&#xa;            if(&quot;hdom&quot;>16,&#xd;&#xa;                -1, &#xd;&#xa;                if(&quot;hdom&quot;>9,&#xd;&#xa;                    -2,&#xd;&#xa;                    -3&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        )&#xd;&#xa;    ),&#xd;&#xa;    if (&quot;VegZone_Code&quot; IN (6, 7),&#xd;&#xa;        if(&quot;NH&quot;>50,&#xd;&#xa;            if(&quot;hdom&quot;>=23, &#xd;&#xa;                if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                    if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                    4,&#xd;&#xa;                        if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                            if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                3,&#xd;&#xa;                                2&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    2,&#xd;&#xa;                                    1&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    1,&#xd;&#xa;                                    0&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    ),&#xd;&#xa;                    5&#xd;&#xa;                ), &#xd;&#xa;                if(&quot;hdom&quot;>16,&#xd;&#xa;                    -1, &#xd;&#xa;                    if(&quot;hdom&quot;>9,&#xd;&#xa;                        -2,&#xd;&#xa;                        -3&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            ),&#xd;&#xa;            if(&quot;hdom&quot;>=19, &#xd;&#xa;                if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                    if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                        if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                            if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                3,&#xd;&#xa;                                2&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    2,&#xd;&#xa;                                    1&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    1,&#xd;&#xa;                                    0&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    ),&#xd;&#xa;                5), &#xd;&#xa;                if(&quot;hdom&quot;>13,&#xd;&#xa;                    -1, &#xd;&#xa;                    if(&quot;hdom&quot;>7,&#xd;&#xa;                        -2,&#xd;&#xa;                        -3&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        ),&#xd;&#xa;        if(&quot;VegZone_Code&quot; IN (8),&#xd;&#xa;            if(&quot;NH&quot;>50,&#xd;&#xa;                if(&quot;hdom&quot;>=19, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                        5&#xd;&#xa;                    ), &#xd;&#xa;                    if(&quot;hdom&quot;>13,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>7,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                if(&quot;hdom&quot;>=16, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                            4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                    5), &#xd;&#xa;                    if(&quot;hdom&quot;>11,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>6,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            ),&#xd;&#xa;            if(&quot;NH&quot;>50,&#xd;&#xa;                if(&quot;hdom&quot;>=16, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                        5&#xd;&#xa;                    ), &#xd;&#xa;                    if(&quot;hdom&quot;>11,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>6,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                if(&quot;hdom&quot;>=13, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                            4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                    5), &#xd;&#xa;                    if(&quot;hdom&quot;>9,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>5,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        )&#xd;&#xa;    )&#xd;&#xa;)&#xd;&#xa;&#xd;&#xa;">
    <categories>
      <category uuid="0" render="true" type="string" label="hdom &lt; 10 * (-3)" value="-3" symbol="0"/>
      <category uuid="1" render="true" type="long" label="10 &lt;= hdom &lt; 18 * (-2)" value="-2" symbol="1"/>
      <category uuid="2" render="true" type="long" label="18 &lt;= hdom &lt; 26 * (-1)" value="-1" symbol="2"/>
      <category uuid="3" render="true" type="long" label="Stabilisierung (0)" value="0" symbol="3"/>
      <category uuid="4" render="true" type="long" label="Nachwuchsförderung (1)" value="1" symbol="4"/>
      <category uuid="5" render="true" type="long" label="Strukturierung (2)" value="2" symbol="5"/>
      <category uuid="6" render="true" type="long" label="Gleichgewicht +/- (3)" value="3" symbol="6"/>
      <category uuid="7" render="true" type="long" label="Struktur geht verloren (zuviel MS) (4)" value="4" symbol="7"/>
      <category uuid="8" render="true" type="long" label="Struktur geht verloren (zuwenig HS) (5)" value="5" symbol="8"/>
      <category uuid="9" render="true" type="string" label="nicht zugeordnet" value="" symbol="9"/>
      <category uuid="10" render="true" type="double" label="" value="-99" symbol="10"/>
      <category uuid="11" render="true" type="double" label="------* hdom Grenzen [m] -------" value="-99" symbol="11"/>
      <category uuid="12" render="true" type="double" label="abhängig von Fokus Nadelholz (NH)/ Laubholz (LH)" value="-99" symbol="12"/>
      <category uuid="13" render="true" type="double" label="und Vegetationshöhenstufe" value="-99" symbol="13"/>
      <category uuid="14" render="true" type="double" label="" value="-99" symbol="14"/>
      <category uuid="15" render="true" type="double" label="Kollin/Sub-/Untermontan (KL,SM,UM): NH 10/18/26 | LH 9/16/23" value="-99" symbol="15"/>
      <category uuid="16" render="true" type="double" label="Obermontan (OM): NH 9/16/23 | LH 7/13/19" value="-99" symbol="16"/>
      <category uuid="17" render="true" type="double" label="Hochmontan (HM): NH 7/13/19 | LH 6/11/16" value="-99" symbol="17"/>
      <category uuid="18" render="true" type="double" label="Subalpin (SA): NH 6 /11/16 | LH 5/9/13" value="-99" symbol="18"/>
      <category uuid="19" render="true" type="double" label="" value="-77" symbol="19"/>
      <category uuid="20" render="true" type="double" label="----------- LABELS -------------" value="-77" symbol="20"/>
      <category uuid="21" render="true" type="double" label="AA.hdom.NH" value="-77" symbol="21"/>
      <category uuid="22" render="true" type="double" label=" x* (yyy)" value="-77" symbol="22"/>
      <category uuid="23" render="true" type="double" label="DG_HS.DG_MS.DG_US.DG_KS" value="-77" symbol="23"/>
      <category uuid="24" render="true" type="double" label="" value="-77" symbol="24"/>
      <category uuid="25" render="true" type="double" label="x: Überführungsphase, *: Anteil KS (>10/ 20/35/55/75)" value="-77" symbol="25"/>
      <category uuid="26" render="true" type="double" label="yyy: Code pro Bestandesstufe" value="-77" symbol="26"/>
      <category uuid="27" render="true" type="double" label="----------------------------------" value="-77" symbol="27"/>
    </categories>
    <symbols>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="0" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{17ace786-dc8f-420e-a520-d94166d43b4b}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="153,204,255,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="1" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{493fba9c-638c-439a-9d45-38e432a911ba}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="0,153,255,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="10" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{d9b734b9-6ba3-4325-acc0-7c186df6a2df}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="11" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{0342b2ba-41b0-4b16-b0e9-afab7c5fef54}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="12" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{35e9da51-64af-4291-9746-6b3440cd612e}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="13" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{a300bb5e-c284-42f0-bb9a-14dbe86038e2}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="14" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{e2a2053d-c085-45ab-999b-6c3659dae08b}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="15" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{6c64c562-26da-4a4c-8c58-d9c73ec7f08f}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="16" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{0eab376c-dbbb-4c41-b0d8-ebbb7318605a}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="17" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{2031a7e3-70f4-46f4-a954-b6b14cc37e5e}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="18" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{aa084ed0-888d-48ad-a474-24cb9ca35fc7}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="19" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{a1ccf9ad-bf76-46e8-8aef-c96c94509fa3}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="2" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{e8d710c6-da4d-4187-8a38-e35897a36c54}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="51,102,204,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="20" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{535f13d7-a6aa-4d4d-ac76-d948546aa5c7}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="21" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{a8ff7ce5-9ef9-4961-b583-49c68e3d540e}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="22" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{4ddd2566-2eca-4dff-935c-56f9b3a6e800}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="183,72,75,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="23" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{003d8b6c-2214-457d-980b-0c2a4b75f34d}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="24" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{e5064251-52b2-4442-8335-3fba44599385}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="231,113,72,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="25" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{3c3f38b1-baa9-4702-ac2e-e22cf7679438}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="26" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{a6d384e9-a714-4bae-b3c8-cb5e7f6f32e1}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="27" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{e12e8f27-35e4-4829-8095-a5ff422cf190}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,0" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="0,0,0,0" name="outline_color"/>
            <Option type="QString" value="no" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="3" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{955f43f9-ecb9-4711-8d61-5651661a7048}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,204,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="4" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{c2f5e083-f866-4fa8-948d-54f1cdf8f347}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,102,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="5" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{ec8c0ae6-a11f-4b58-8e43-79b47898af5b}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="204,255,51,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="6" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{1946cd9c-8495-41ab-a1e9-421317b9f2a0}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="56,168,0,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="7" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{597f0ade-c669-4b4f-b081-3ba7589b64f5}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,204,0,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="8" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{7b45b847-dfde-4c9e-ad73-d6dd567d70ea}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,102,0,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="9" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{de241ca3-b650-40c1-86a1-3b7f760f1a91}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="255,255,255,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="0" force_rhr="0" frame_rate="10" alpha="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{2a736a29-326b-45cd-97ac-a27c9201fec2}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="141,90,153,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="no" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol is_animated="0" type="fill" clip_to_extent="1" name="" force_rhr="0" frame_rate="10" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </data_defined_properties>
        <layer id="{70984f71-6d2a-481e-85ee-8c7b898ed4a7}" locked="0" class="SimpleFill" enabled="1" pass="0">
          <Option type="Map">
            <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
            <Option type="QString" value="0,0,255,255" name="color"/>
            <Option type="QString" value="bevel" name="joinstyle"/>
            <Option type="QString" value="0,0" name="offset"/>
            <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
            <Option type="QString" value="MM" name="offset_unit"/>
            <Option type="QString" value="35,35,35,255" name="outline_color"/>
            <Option type="QString" value="solid" name="outline_style"/>
            <Option type="QString" value="0.26" name="outline_width"/>
            <Option type="QString" value="MM" name="outline_width_unit"/>
            <Option type="QString" value="solid" name="style"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style forcedBold="0" useSubstitutions="0" fontSize="7" isExpression="1" allowHtml="0" fontItalic="0" capitalization="0" fontUnderline="0" legendString="Aa" forcedItalic="0" fontKerning="1" fontLetterSpacing="0" fontWeight="50" blendMode="0" fontWordSpacing="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" previewBkgrdColor="255,255,255,255" fontStrikeout="0" namedStyle="Standard" textOrientation="horizontal" multilineHeightUnit="Percentage" textColor="0,0,0,255" fontSizeUnit="Point" fieldName="if(&quot;VegZone_Code&quot; IN (2), &#xd;&#xa;    'KL',&#xd;&#xa;    if(&quot;VegZone_Code&quot; IN (4),&#xd;&#xa;        'SM',&#xd;&#xa;        if(&quot;VegZone_Code&quot; IN (5),&#xd;&#xa;            'UM',&#xd;&#xa;            if(&quot;VegZone_Code&quot; IN (6, 7),&#xd;&#xa;                'OM',&#xd;&#xa;                if(&quot;VegZone_Code&quot; IN (8),&#xd;&#xa;                    'HM',&#xd;&#xa;                     if(&quot;VegZone_Code&quot; IN (9),&#xd;&#xa;                    'SA',&#xd;&#xa;                    '??'&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        )    &#xd;&#xa;    )&#xd;&#xa;) + '.' + &#xd;&#xa;to_string(&quot;hdom&quot;) + '.' + &#xd;&#xa;to_string(to_int(round(to_real(&quot;NH&quot;)/10))) + &#xd;&#xa;&#xd;&#xa;'\n' + &#xd;&#xa;&#xd;&#xa;to_string(&#xd;&#xa;if(&quot;VegZone&quot; IN (-1, 0, 1, 2, 4, 5), &#xd;&#xa;    if(&quot;NH&quot;>50,&#xd;&#xa;        if(&quot;hdom&quot;>=26, &#xd;&#xa;            if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                4,&#xd;&#xa;                    if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                        if(&quot;DG_us&quot; >=20,&#xd;&#xa;                            3,&#xd;&#xa;                            2&#xd;&#xa;                        ),&#xd;&#xa;                        if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                2,&#xd;&#xa;                                1&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                1,&#xd;&#xa;                                0&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                5&#xd;&#xa;            ), &#xd;&#xa;            if(&quot;hdom&quot;>18,&#xd;&#xa;                -1, &#xd;&#xa;                if(&quot;hdom&quot;>10,&#xd;&#xa;                    -2,&#xd;&#xa;                    -3&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        ),&#xd;&#xa;        if(&quot;hdom&quot;>=23, &#xd;&#xa;            if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                    4,&#xd;&#xa;                    if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                        if(&quot;DG_us&quot; >=20,&#xd;&#xa;                            3,&#xd;&#xa;                            2&#xd;&#xa;                        ),&#xd;&#xa;                        if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                2,&#xd;&#xa;                                1&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                1,&#xd;&#xa;                                0&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;            5), &#xd;&#xa;            if(&quot;hdom&quot;>16,&#xd;&#xa;                -1, &#xd;&#xa;                if(&quot;hdom&quot;>9,&#xd;&#xa;                    -2,&#xd;&#xa;                    -3&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        )&#xd;&#xa;    ),&#xd;&#xa;    if (&quot;VegZone_Code&quot; IN (6, 7),&#xd;&#xa;        if(&quot;NH&quot;>50,&#xd;&#xa;            if(&quot;hdom&quot;>=23, &#xd;&#xa;                if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                    if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                    4,&#xd;&#xa;                        if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                            if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                3,&#xd;&#xa;                                2&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    2,&#xd;&#xa;                                    1&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    1,&#xd;&#xa;                                    0&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    ),&#xd;&#xa;                    5&#xd;&#xa;                ), &#xd;&#xa;                if(&quot;hdom&quot;>16,&#xd;&#xa;                    -1, &#xd;&#xa;                    if(&quot;hdom&quot;>9,&#xd;&#xa;                        -2,&#xd;&#xa;                        -3&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            ),&#xd;&#xa;            if(&quot;hdom&quot;>=19, &#xd;&#xa;                if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                    if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                        if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                            if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                3,&#xd;&#xa;                                2&#xd;&#xa;                            ),&#xd;&#xa;                            if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    2,&#xd;&#xa;                                    1&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                    1,&#xd;&#xa;                                    0&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        )&#xd;&#xa;                    ),&#xd;&#xa;                5), &#xd;&#xa;                if(&quot;hdom&quot;>13,&#xd;&#xa;                    -1, &#xd;&#xa;                    if(&quot;hdom&quot;>7,&#xd;&#xa;                        -2,&#xd;&#xa;                        -3&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        ),&#xd;&#xa;        if(&quot;VegZone_Code&quot; IN (8),&#xd;&#xa;            if(&quot;NH&quot;>50,&#xd;&#xa;                if(&quot;hdom&quot;>=19, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                        5&#xd;&#xa;                    ), &#xd;&#xa;                    if(&quot;hdom&quot;>13,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>7,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                if(&quot;hdom&quot;>=16, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                            4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                    5), &#xd;&#xa;                    if(&quot;hdom&quot;>11,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>6,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            ),&#xd;&#xa;            if(&quot;NH&quot;>50,&#xd;&#xa;                if(&quot;hdom&quot;>=16, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                        4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                        5&#xd;&#xa;                    ), &#xd;&#xa;                    if(&quot;hdom&quot;>11,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>6,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                ),&#xd;&#xa;                if(&quot;hdom&quot;>=13, &#xd;&#xa;                    if(&quot;DG_os&quot; + &quot;DG_ueb&quot; >= 45, &#xd;&#xa;                        if(&quot;DG_ms&quot; >= 35,&#xd;&#xa;                            4,&#xd;&#xa;                            if(&quot;DG_ms&quot;>=25,&#xd;&#xa;                                if(&quot;DG_us&quot; >=20,&#xd;&#xa;                                    3,&#xd;&#xa;                                    2&#xd;&#xa;                                ),&#xd;&#xa;                                if(&quot;DG_ms&quot;>=15,&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        2,&#xd;&#xa;                                        1&#xd;&#xa;                                    ),&#xd;&#xa;                                    if(&quot;DG_us&quot;>=10,&#xd;&#xa;                                        1,&#xd;&#xa;                                        0&#xd;&#xa;                                    )&#xd;&#xa;                                )&#xd;&#xa;                            )&#xd;&#xa;                        ),&#xd;&#xa;                    5), &#xd;&#xa;                    if(&quot;hdom&quot;>9,&#xd;&#xa;                        -1, &#xd;&#xa;                        if(&quot;hdom&quot;>5,&#xd;&#xa;                            -2,&#xd;&#xa;                            -3&#xd;&#xa;                        )&#xd;&#xa;                    )&#xd;&#xa;                )&#xd;&#xa;            )&#xd;&#xa;        )&#xd;&#xa;    )&#xd;&#xa;)&#xd;&#xa;) + &#xd;&#xa;&#xd;&#xa;if(&quot;DG_ks&quot; > 10, '*','')  + &#xd;&#xa;if(&quot;DG_ks&quot; > 20, '*','')  + &#xd;&#xa;if(&quot;DG_ks&quot; > 35, '*','')  + &#xd;&#xa;if(&quot;DG_ks&quot; > 55, '*','')  + &#xd;&#xa;if(&quot;DG_ks&quot; > 75, '*','')  + &#xd;&#xa;&#xd;&#xa;'(' + &#xd;&#xa;&#xd;&#xa;to_string(if(&quot;DG_os&quot; + &quot;DG_ueb&quot; &lt; 35, 5, if(&quot;DG_os&quot; + &quot;DG_ueb&quot; &lt;45, 4, if(&quot;DG_os&quot; + &quot;DG_ueb&quot; &lt;= 55, 3, if(&quot;DG_os&quot; + &quot;DG_ueb&quot; &lt; 70, 2, if(&quot;DG_os&quot; + &quot;DG_ueb&quot; &lt; 85, 1, 0)))))) + &#xd;&#xa;&#xd;&#xa;to_string(if(&quot;DG_ms&quot; > 45, 5, if(&quot;DG_ms&quot; > 35, 4, if(&quot;DG_ms&quot; >= 25, 3, if(&quot;DG_ms&quot; >= 15, 2, if(&quot;DG_ms&quot; >= 5, 1, 0)))))) + &#xd;&#xa;&#xd;&#xa;to_string(if(&quot;DG_us&quot; > 40, 5, if(&quot;DG_us&quot; > 30, 4, if(&quot;DG_us&quot; >= 20, 3, if(&quot;DG_us&quot; >= 10, 2, if(&quot;DG_us&quot; > 1, 1, 0)))))) +&#xd;&#xa;&#xd;&#xa;')' + &#xd;&#xa; &#xd;&#xa;'\n' + &#xd;&#xa;to_string(&quot;DG_os&quot; + &quot;DG_ueb&quot;) + '.' + &#xd;&#xa;to_string(&quot;DG_ms&quot;) + '.' + &#xd;&#xa;to_string(&quot;DG_us&quot;) + '.' + &#xd;&#xa;to_string(&quot;DG_ks&quot;)" fontFamily="MS Shell Dlg 2" textOpacity="1" multilineHeight="1">
        <families/>
        <text-buffer bufferSize="1" bufferOpacity="1" bufferBlendMode="0" bufferSizeUnits="MM" bufferNoFill="1" bufferJoinStyle="128" bufferDraw="0" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255"/>
        <text-mask maskEnabled="0" maskOpacity="1" maskType="0" maskSizeUnits="MM" maskJoinStyle="128" maskedSymbolLayers="" maskSize="1.5" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <background shapeSVGFile="" shapeSizeX="0" shapeDraw="0" shapeOpacity="1" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeOffsetUnit="MM" shapeFillColor="255,255,255,255" shapeBorderWidth="0" shapeBlendMode="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeRadiiUnit="MM" shapeType="0" shapeRadiiX="0" shapeRadiiY="0" shapeBorderWidthUnit="MM" shapeRotationType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255" shapeJoinStyle="64" shapeSizeType="0" shapeOffsetX="0" shapeSizeY="0" shapeRotation="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0">
          <symbol is_animated="0" type="marker" clip_to_extent="1" name="markerSymbol" force_rhr="0" frame_rate="10" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer id="" locked="0" class="SimpleMarker" enabled="1" pass="0">
              <Option type="Map">
                <Option type="QString" value="0" name="angle"/>
                <Option type="QString" value="square" name="cap_style"/>
                <Option type="QString" value="183,72,75,255" name="color"/>
                <Option type="QString" value="1" name="horizontal_anchor_point"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="circle" name="name"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="35,35,35,255" name="outline_color"/>
                <Option type="QString" value="solid" name="outline_style"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="diameter" name="scale_method"/>
                <Option type="QString" value="2" name="size"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="size_map_unit_scale"/>
                <Option type="QString" value="MM" name="size_unit"/>
                <Option type="QString" value="1" name="vertical_anchor_point"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol is_animated="0" type="fill" clip_to_extent="1" name="fillSymbol" force_rhr="0" frame_rate="10" alpha="1">
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
            <layer id="" locked="0" class="SimpleFill" enabled="1" pass="0">
              <Option type="Map">
                <Option type="QString" value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale"/>
                <Option type="QString" value="255,255,255,255" name="color"/>
                <Option type="QString" value="bevel" name="joinstyle"/>
                <Option type="QString" value="0,0" name="offset"/>
                <Option type="QString" value="3x:0,0,0,0,0,0" name="offset_map_unit_scale"/>
                <Option type="QString" value="MM" name="offset_unit"/>
                <Option type="QString" value="128,128,128,255" name="outline_color"/>
                <Option type="QString" value="no" name="outline_style"/>
                <Option type="QString" value="0" name="outline_width"/>
                <Option type="QString" value="MM" name="outline_width_unit"/>
                <Option type="QString" value="solid" name="style"/>
              </Option>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetDist="1" shadowOffsetUnit="MM" shadowRadiusAlphaOnly="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowRadius="1.5" shadowColor="0,0,0,255" shadowOpacity="0.69999999999999996" shadowUnder="0" shadowDraw="0" shadowOffsetAngle="135" shadowScale="100" shadowBlendMode="6" shadowOffsetGlobal="1" shadowRadiusUnit="MM"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" formatNumbers="0" rightDirectionSymbol=">" addDirectionSymbol="0" wrapChar="" decimals="3" useMaxLineLengthForAutoWrap="1" multilineAlign="3" autoWrapLength="0" plussign="0" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0"/>
      <placement repeatDistance="0" lineAnchorTextPoint="CenterOfText" centroidInside="1" centroidWhole="0" lineAnchorClipping="0" overrunDistance="0" maxCurvedCharAngleOut="-25" priority="5" placementFlags="10" allowDegraded="0" yOffset="0" polygonPlacementFlags="2" dist="0" lineAnchorType="0" geometryGenerator="" overlapHandling="PreventOverlap" maxCurvedCharAngleIn="25" rotationUnit="AngleDegrees" offsetUnits="MM" xOffset="0" preserveRotation="1" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" rotationAngle="0" quadOffset="4" placement="1" geometryGeneratorType="PointGeometry" fitInPolygonOnly="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" repeatDistanceUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" layerType="PolygonGeometry" distUnits="MM" lineAnchorPercent="0.5" distMapUnitScale="3x:0,0,0,0,0,0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceUnit="MM" offsetType="0" geometryGeneratorEnabled="0"/>
      <rendering fontMaxPixelSize="10000" obstacleFactor="1" fontLimitPixelSize="0" obstacle="1" mergeLines="0" upsidedownLabels="0" maxNumLabels="2000" zIndex="0" scaleMax="5001" limitNumLabels="0" minFeatureSize="0" scaleVisibility="1" fontMinPixelSize="3" labelPerPart="0" drawLabels="1" obstacleType="1" unplacedVisibility="0" scaleMin="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" value="" name="name"/>
          <Option name="properties"/>
          <Option type="QString" value="collection" name="type"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
          <Option type="int" value="0" name="blendMode"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
          <Option type="bool" value="false" name="drawToAllParts"/>
          <Option type="QString" value="0" name="enabled"/>
          <Option type="QString" value="point_on_exterior" name="labelAnchorPoint"/>
          <Option type="QString" value="&lt;symbol is_animated=&quot;0&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot; name=&quot;symbol&quot; force_rhr=&quot;0&quot; frame_rate=&quot;10&quot; alpha=&quot;1&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer id=&quot;{ca1eb9d2-c31f-4904-a5dd-94c6b1143d10}&quot; locked=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot; pass=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;align_dash_pattern&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;square&quot; name=&quot;capstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;5;2&quot; name=&quot;customdash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;customdash_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;customdash_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;dash_pattern_offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;dash_pattern_offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;draw_inside_polygon&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;bevel&quot; name=&quot;joinstyle&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;60,60,60,255&quot; name=&quot;line_color&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;solid&quot; name=&quot;line_style&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0.3&quot; name=&quot;line_width&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;line_width_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;offset&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;offset_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;offset_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;ring_filter&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_end&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_end_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_end_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;trim_distance_start&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_start_map_unit_scale&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;MM&quot; name=&quot;trim_distance_start_unit&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;0&quot; name=&quot;use_custom_dash&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;width_map_unit_scale&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
          <Option type="double" value="0" name="minLength"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
          <Option type="QString" value="MM" name="minLengthUnit"/>
          <Option type="double" value="0" name="offsetFromAnchor"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
          <Option type="double" value="0" name="offsetFromLabel"/>
          <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
          <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
