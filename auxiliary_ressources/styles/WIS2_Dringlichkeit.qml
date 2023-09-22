<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" labelsEnabled="0" simplifyDrawingHints="1" version="3.16.11-Hannover" simplifyLocal="1" simplifyMaxScale="1" readOnly="0" minScale="100000000" hasScaleBasedVisibilityFlag="0" maxScale="0" simplifyAlgorithm="0" simplifyDrawingTol="1">
  <renderer-3d type="rulebased" layer="TBk_Bestandeskarte_Verjuegung_Kopie_78b3e781_f2b8_4fbb_a089_af4512a189c9">
    <vector-layer-3d-tiling zoom-levels-count="3" show-bounding-boxes="0"/>
    <rules key="{f58edf58-cedf-48fc-8203-8dbfca44a307}"/>
  </renderer-3d>
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endExpression="" endField="" mode="0" startField="" enabled="0" durationUnit="min" accumulate="0" fixedDuration="0" startExpression="" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="RuleRenderer" symbollevels="0" forceraster="0" enableorderby="0">
    <rules key="{1ec9c0b9-224f-4811-8363-1d3da9d99aac}">
      <rule key="{dc75a223-e3ae-479d-83ff-05b84835c09a}" label="Dringlichkeit &lt;= 0 J:" filter="(&quot;W2C_Out_VJG_Total_0j_ha&quot; = 0 AND  &quot;W2C_Out_VJG_Total_10j_ha&quot; =0) AND (&quot;DGUe90_mea&quot; *  &quot;area_m2&quot; >= 2500 OR (&quot;area_m2&quot; &lt; 5000 AND &quot;DGUe90_mea&quot; >= 0.5)) " symbol="0">
        <rule key="{e720b692-6712-4478-b859-2da87307f758}" label="> 75% der Fläche mit  DG>=90%" filter="&quot;DGUe90_mea&quot; >0.75" symbol="1"/>
        <rule key="{17d2947f-c4fe-40ba-9735-f5410fcad741}" label="50-75% der Fläche mit  DG>=90%" filter="&quot;DGUe90_mea&quot; > 0.5 AND &quot;DGUe90_mea&quot; &lt;= 0.75" symbol="2"/>
        <rule key="{f553951c-2ef1-448d-9aa5-82d258a6149c}" label="25-50% der Fläche mit  DG>=90%" filter="&quot;DGUe90_mea&quot; > 0.25 AND &quot;DGUe90_mea&quot; &lt;= 0.5" symbol="3"/>
        <rule key="{fbe84a32-ce83-42d0-8cea-c66ea8ce761e}" label="10-25% der Fläche mit  DG>=90%" filter="&quot;DGUe90_mea&quot; > 0.10 AND &quot;DGUe90_mea&quot; &lt;=0.25" symbol="4"/>
      </rule>
      <rule key="{6acd44f8-391a-46da-8903-767656b68d2e}" label="Dringlichkeit 1 - 3 J:" filter=" &quot;W2C_Out_DFG_Total_3j_ha&quot; > 0" symbol="5">
        <rule key="{6a410a00-b9fa-46ab-be4f-3bdc0ea1a1f8}" label="1 - 25% der Fläche" filter="( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) >= 0.010000 AND ( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.250000" symbol="6"/>
        <rule key="{dbd2f9e2-55c7-447a-b3b3-ff1ef317629e}" label="26 - 50% der Fläche" filter="( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.250000 AND ( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.500000" symbol="7"/>
        <rule key="{b4233118-0257-4432-9f1a-c2d7963a4b9e}" label="51 - 75% der Fläche" filter="( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.500000 AND ( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.750000" symbol="8"/>
        <rule key="{9e9d63f2-5938-499f-82c5-7600326048db}" label="76 - 100% der Fläche" filter="( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.750000 AND ( &quot;W2C_Out_DFG_Total_3j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 1.000000" symbol="9"/>
      </rule>
      <rule key="{851df3ab-0b5e-4e57-9833-82b05ad2bfaa}" label="Dringlichkeit 4 - 6 J:" filter=" &quot;W2C_Out_DFG_Total_6j_ha&quot; > 0" symbol="10">
        <rule key="{7730ad35-5995-4424-aa02-b48de15ceafb}" label="1 - 25% der Fläche" filter="( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) >= 0.010000 AND ( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.250000" symbol="11"/>
        <rule key="{fc882b79-3861-4c3c-9113-e0322b74f36f}" label="26 - 50% der Fläche" filter="( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.250000 AND ( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.500000" symbol="12"/>
        <rule key="{5bbfede9-5ab8-4373-9569-2975941ee23a}" label="51 - 75% der Fläche" filter="( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.500000 AND ( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.750000" symbol="13"/>
        <rule key="{805ad6dd-aa94-44b0-b56a-5922d5804c9d}" label="76 - 100% der Fläche" filter="( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.750000 AND ( &quot;W2C_Out_DFG_Total_6j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 1.000000" symbol="14"/>
      </rule>
      <rule key="{e981a50f-38e7-48da-a75c-0eb43e6de3a4}" label="Dringlichkeit 7 - 10 J:" filter=" &quot;W2C_Out_DFG_Total_10j_ha&quot; > 0" symbol="15">
        <rule key="{94e6cb1f-b808-4ecf-8ab1-4d749117f87f}" label="1 - 25% der Fläche" filter="( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) >= 0.010000 AND ( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.250000" symbol="16"/>
        <rule key="{2d59630c-048c-4658-a396-c5b9d399fb64}" label="26 - 50% der Fläche" filter="( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.250000 AND ( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.500000" symbol="17"/>
        <rule key="{8d2ba649-34f3-44c6-a7ac-87a4ce48770d}" label="51 - 75% der Fläche" filter="( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.500000 AND ( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 0.750000" symbol="18"/>
        <rule key="{dfec6651-c9d9-4b0d-b143-0f0a937ec26a}" label="76 - 100% der Fläche" filter="( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) > 0.750000 AND ( &quot;W2C_Out_DFG_Total_10j_ha&quot; /  &quot;W2C_Out_bst_ha&quot; ) &lt;= 1.000000" symbol="19"/>
      </rule>
    </rules>
    <symbols>
      <symbol name="0" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="133,182,111,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="1" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="dense4" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="10" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="133,182,111,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="11" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="0" k="angle"/>
          <prop v="129,164,205,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@11@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="129,164,205,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="12" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="0" k="angle"/>
          <prop v="129,164,205,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@12@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="129,164,205,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="13" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="0" k="angle"/>
          <prop v="129,164,205,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@13@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="129,164,205,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="14" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="0" k="angle"/>
          <prop v="129,164,205,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@14@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="129,164,205,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="2" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="15" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="133,182,111,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="16" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="-45" k="angle"/>
          <prop v="219,228,238,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@16@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="219,228,238,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="17" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="-45" k="angle"/>
          <prop v="219,228,238,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@17@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="219,228,238,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="18" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="-45" k="angle"/>
          <prop v="219,228,238,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@18@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="219,228,238,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="19" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="-45" k="angle"/>
          <prop v="219,228,238,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@19@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="219,228,238,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="2" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="2" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="dense5" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="3" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="dense6" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="4" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="dense7" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="5" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="133,182,111,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="6" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="45" k="angle"/>
          <prop v="62,124,177,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@6@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="62,124,177,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="0.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="7" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="45" k="angle"/>
          <prop v="62,124,177,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@7@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="62,124,177,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="8" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="45" k="angle"/>
          <prop v="62,124,177,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@8@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="62,124,177,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="1.5" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol name="9" type="fill" force_rhr="0" clip_to_extent="1" alpha="1">
        <layer pass="0" locked="0" enabled="1" class="LinePatternFill">
          <prop v="45" k="angle"/>
          <prop v="62,124,177,255" k="color"/>
          <prop v="5" k="distance"/>
          <prop v="3x:0,0,0,0,0,0" k="distance_map_unit_scale"/>
          <prop v="MM" k="distance_unit"/>
          <prop v="0.26" k="line_width"/>
          <prop v="3x:0,0,0,0,0,0" k="line_width_map_unit_scale"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol name="@9@0" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
            <layer pass="0" locked="0" enabled="1" class="SimpleLine">
              <prop v="0" k="align_dash_pattern"/>
              <prop v="square" k="capstyle"/>
              <prop v="5;2" k="customdash"/>
              <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
              <prop v="MM" k="customdash_unit"/>
              <prop v="0" k="dash_pattern_offset"/>
              <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
              <prop v="MM" k="dash_pattern_offset_unit"/>
              <prop v="0" k="draw_inside_polygon"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="62,124,177,255" k="line_color"/>
              <prop v="solid" k="line_style"/>
              <prop v="2" k="line_width"/>
              <prop v="MM" k="line_width_unit"/>
              <prop v="0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="0" k="ring_filter"/>
              <prop v="0" k="tweak_dash_pattern_on_corners"/>
              <prop v="0" k="use_custom_dash"/>
              <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property value="&quot;ID&quot;" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory minScaleDenominator="0" backgroundAlpha="255" spacing="0" opacity="1" scaleBasedVisibility="0" spacingUnit="MM" direction="1" enabled="0" backgroundColor="#ffffff" diagramOrientation="Up" lineSizeType="MM" spacingUnitScale="3x:0,0,0,0,0,0" sizeType="MM" sizeScale="3x:0,0,0,0,0,0" width="15" scaleDependency="Area" rotationOffset="270" showAxis="0" penAlpha="255" penWidth="0" labelPlacementMethod="XHeight" height="15" lineSizeScale="3x:0,0,0,0,0,0" barWidth="5" minimumSize="0" maxScaleDenominator="1e+08" penColor="#000000">
      <fontProperties style="" description="MS Shell Dlg 2,7.875,-1,5,50,0,0,0,0,0"/>
      <attribute field="" color="#000000" label=""/>
      <axisSymbol>
        <symbol name="" type="line" force_rhr="0" clip_to_extent="1" alpha="1">
          <layer pass="0" locked="0" enabled="1" class="SimpleLine">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" obstacle="0" dist="0" priority="0" placement="1" showAll="1" zIndex="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option value="0" name="allowedGapsBuffer" type="double"/>
        <Option value="false" name="allowedGapsEnabled" type="bool"/>
        <Option value="" name="allowedGapsLayer" type="QString"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="area_m2" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="ID" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="hmax" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="hdom" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ks_coun" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ks_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_us_coun" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_us_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ms_coun" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ms_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_os_coun" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_os_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ueb_cou" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_ueb_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_count" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dg_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG_ks" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG_us" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG_ms" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG_os" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG_ueb" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DG" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nh_count" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nh_sum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NH" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nh_count_1" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nh_sum_1" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nhm_count" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nhm_mean" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NH_OS" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NH_OS_PIX" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nr" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="struktur" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="tbk_typ" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="frehner63" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="WG_WIS2" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_SP" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_ddom_IST" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_hdom_IST" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_Station" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_Age" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_bst_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_letzterEingriff" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_typ" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Fi" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Ta" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Fö" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Lä" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_üN" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Bu" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Ei" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Es" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_Ah" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_MS_üL" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_3j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_6j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_10j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_3j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_6j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Total_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Total_0j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Total_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Total_20j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Total_30j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_3j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_6j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_10j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_3j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_6j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fi_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fi_0j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fi_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fi_20j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fi_30j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ta_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ta_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ta_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ta_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ta_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Fö_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fö_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fö_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fö_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Fö_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Lä_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Lä_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Lä_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Lä_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Lä_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üN_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üN_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üN_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üN_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üN_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_3j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_6j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_10j_Tfm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_3j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_6j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Bu_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Bu_0j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Bu_10j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Bu_20j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Bu_30j_ha" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ei_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ei_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ei_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ei_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ei_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Es_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Es_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Es_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Es_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Es_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_Ah_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ah_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ah_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ah_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_Ah_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_0j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_3j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_6j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_10j_Tfm" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_3j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_6j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_DFG_üL_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üL_0j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üL_10j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üL_20j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="W2C_Out_VJG_üL_30j_ha" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" field="area_m2" index="0"/>
    <alias name="" field="ID" index="1"/>
    <alias name="" field="hmax" index="2"/>
    <alias name="" field="hdom" index="3"/>
    <alias name="" field="dg_ks_coun" index="4"/>
    <alias name="" field="dg_ks_sum" index="5"/>
    <alias name="" field="dg_us_coun" index="6"/>
    <alias name="" field="dg_us_sum" index="7"/>
    <alias name="" field="dg_ms_coun" index="8"/>
    <alias name="" field="dg_ms_sum" index="9"/>
    <alias name="" field="dg_os_coun" index="10"/>
    <alias name="" field="dg_os_sum" index="11"/>
    <alias name="" field="dg_ueb_cou" index="12"/>
    <alias name="" field="dg_ueb_sum" index="13"/>
    <alias name="" field="dg_count" index="14"/>
    <alias name="" field="dg_sum" index="15"/>
    <alias name="" field="DG_ks" index="16"/>
    <alias name="" field="DG_us" index="17"/>
    <alias name="" field="DG_ms" index="18"/>
    <alias name="" field="DG_os" index="19"/>
    <alias name="" field="DG_ueb" index="20"/>
    <alias name="" field="DG" index="21"/>
    <alias name="" field="nh_count" index="22"/>
    <alias name="" field="nh_sum" index="23"/>
    <alias name="" field="NH" index="24"/>
    <alias name="" field="nh_count_1" index="25"/>
    <alias name="" field="nh_sum_1" index="26"/>
    <alias name="" field="nhm_count" index="27"/>
    <alias name="" field="nhm_mean" index="28"/>
    <alias name="" field="NH_OS" index="29"/>
    <alias name="" field="NH_OS_PIX" index="30"/>
    <alias name="" field="nr" index="31"/>
    <alias name="" field="struktur" index="32"/>
    <alias name="" field="tbk_typ" index="33"/>
    <alias name="" field="frehner63" index="34"/>
    <alias name="" field="WG_WIS2" index="35"/>
    <alias name="" field="W2C_Out_SP" index="36"/>
    <alias name="" field="W2C_Out_ddom_IST" index="37"/>
    <alias name="" field="W2C_Out_hdom_IST" index="38"/>
    <alias name="" field="W2C_Out_Station" index="39"/>
    <alias name="" field="W2C_Out_Age" index="40"/>
    <alias name="" field="W2C_Out_bst_ha" index="41"/>
    <alias name="" field="W2C_Out_letzterEingriff" index="42"/>
    <alias name="" field="W2C_Out_MS_typ" index="43"/>
    <alias name="" field="W2C_Out_MS_Fi" index="44"/>
    <alias name="" field="W2C_Out_MS_Ta" index="45"/>
    <alias name="" field="W2C_Out_MS_Fö" index="46"/>
    <alias name="" field="W2C_Out_MS_Lä" index="47"/>
    <alias name="" field="W2C_Out_MS_üN" index="48"/>
    <alias name="" field="W2C_Out_MS_Bu" index="49"/>
    <alias name="" field="W2C_Out_MS_Ei" index="50"/>
    <alias name="" field="W2C_Out_MS_Es" index="51"/>
    <alias name="" field="W2C_Out_MS_Ah" index="52"/>
    <alias name="" field="W2C_Out_MS_üL" index="53"/>
    <alias name="" field="W2C_Out_DFG_Total_0j_Tfm" index="54"/>
    <alias name="" field="W2C_Out_DFG_Total_3j_Tfm" index="55"/>
    <alias name="" field="W2C_Out_DFG_Total_6j_Tfm" index="56"/>
    <alias name="" field="W2C_Out_DFG_Total_10j_Tfm" index="57"/>
    <alias name="" field="W2C_Out_DFG_Total_0j_ha" index="58"/>
    <alias name="" field="W2C_Out_DFG_Total_3j_ha" index="59"/>
    <alias name="" field="W2C_Out_DFG_Total_6j_ha" index="60"/>
    <alias name="" field="W2C_Out_DFG_Total_10j_ha" index="61"/>
    <alias name="" field="W2C_Out_VJG_Total_0j_ha" index="62"/>
    <alias name="" field="W2C_Out_VJG_Total_10j_ha" index="63"/>
    <alias name="" field="W2C_Out_VJG_Total_20j_ha" index="64"/>
    <alias name="" field="W2C_Out_VJG_Total_30j_ha" index="65"/>
    <alias name="" field="W2C_Out_DFG_Fi_0j_Tfm" index="66"/>
    <alias name="" field="W2C_Out_DFG_Fi_3j_Tfm" index="67"/>
    <alias name="" field="W2C_Out_DFG_Fi_6j_Tfm" index="68"/>
    <alias name="" field="W2C_Out_DFG_Fi_10j_Tfm" index="69"/>
    <alias name="" field="W2C_Out_DFG_Fi_0j_ha" index="70"/>
    <alias name="" field="W2C_Out_DFG_Fi_3j_ha" index="71"/>
    <alias name="" field="W2C_Out_DFG_Fi_6j_ha" index="72"/>
    <alias name="" field="W2C_Out_DFG_Fi_10j_ha" index="73"/>
    <alias name="" field="W2C_Out_VJG_Fi_0j_ha" index="74"/>
    <alias name="" field="W2C_Out_VJG_Fi_10j_ha" index="75"/>
    <alias name="" field="W2C_Out_VJG_Fi_20j_ha" index="76"/>
    <alias name="" field="W2C_Out_VJG_Fi_30j_ha" index="77"/>
    <alias name="" field="W2C_Out_DFG_Ta_0j_Tfm" index="78"/>
    <alias name="" field="W2C_Out_DFG_Ta_3j_Tfm" index="79"/>
    <alias name="" field="W2C_Out_DFG_Ta_6j_Tfm" index="80"/>
    <alias name="" field="W2C_Out_DFG_Ta_10j_Tfm" index="81"/>
    <alias name="" field="W2C_Out_DFG_Ta_0j_ha" index="82"/>
    <alias name="" field="W2C_Out_DFG_Ta_3j_ha" index="83"/>
    <alias name="" field="W2C_Out_DFG_Ta_6j_ha" index="84"/>
    <alias name="" field="W2C_Out_DFG_Ta_10j_ha" index="85"/>
    <alias name="" field="W2C_Out_VJG_Ta_0j_ha" index="86"/>
    <alias name="" field="W2C_Out_VJG_Ta_10j_ha" index="87"/>
    <alias name="" field="W2C_Out_VJG_Ta_20j_ha" index="88"/>
    <alias name="" field="W2C_Out_VJG_Ta_30j_ha" index="89"/>
    <alias name="" field="W2C_Out_DFG_Fö_0j_Tfm" index="90"/>
    <alias name="" field="W2C_Out_DFG_Fö_3j_Tfm" index="91"/>
    <alias name="" field="W2C_Out_DFG_Fö_6j_Tfm" index="92"/>
    <alias name="" field="W2C_Out_DFG_Fö_10j_Tfm" index="93"/>
    <alias name="" field="W2C_Out_DFG_Fö_0j_ha" index="94"/>
    <alias name="" field="W2C_Out_DFG_Fö_3j_ha" index="95"/>
    <alias name="" field="W2C_Out_DFG_Fö_6j_ha" index="96"/>
    <alias name="" field="W2C_Out_DFG_Fö_10j_ha" index="97"/>
    <alias name="" field="W2C_Out_VJG_Fö_0j_ha" index="98"/>
    <alias name="" field="W2C_Out_VJG_Fö_10j_ha" index="99"/>
    <alias name="" field="W2C_Out_VJG_Fö_20j_ha" index="100"/>
    <alias name="" field="W2C_Out_VJG_Fö_30j_ha" index="101"/>
    <alias name="" field="W2C_Out_DFG_Lä_0j_Tfm" index="102"/>
    <alias name="" field="W2C_Out_DFG_Lä_3j_Tfm" index="103"/>
    <alias name="" field="W2C_Out_DFG_Lä_6j_Tfm" index="104"/>
    <alias name="" field="W2C_Out_DFG_Lä_10j_Tfm" index="105"/>
    <alias name="" field="W2C_Out_DFG_Lä_0j_ha" index="106"/>
    <alias name="" field="W2C_Out_DFG_Lä_3j_ha" index="107"/>
    <alias name="" field="W2C_Out_DFG_Lä_6j_ha" index="108"/>
    <alias name="" field="W2C_Out_DFG_Lä_10j_ha" index="109"/>
    <alias name="" field="W2C_Out_VJG_Lä_0j_ha" index="110"/>
    <alias name="" field="W2C_Out_VJG_Lä_10j_ha" index="111"/>
    <alias name="" field="W2C_Out_VJG_Lä_20j_ha" index="112"/>
    <alias name="" field="W2C_Out_VJG_Lä_30j_ha" index="113"/>
    <alias name="" field="W2C_Out_DFG_üN_0j_Tfm" index="114"/>
    <alias name="" field="W2C_Out_DFG_üN_3j_Tfm" index="115"/>
    <alias name="" field="W2C_Out_DFG_üN_6j_Tfm" index="116"/>
    <alias name="" field="W2C_Out_DFG_üN_10j_Tfm" index="117"/>
    <alias name="" field="W2C_Out_DFG_üN_0j_ha" index="118"/>
    <alias name="" field="W2C_Out_DFG_üN_3j_ha" index="119"/>
    <alias name="" field="W2C_Out_DFG_üN_6j_ha" index="120"/>
    <alias name="" field="W2C_Out_DFG_üN_10j_ha" index="121"/>
    <alias name="" field="W2C_Out_VJG_üN_0j_ha" index="122"/>
    <alias name="" field="W2C_Out_VJG_üN_10j_ha" index="123"/>
    <alias name="" field="W2C_Out_VJG_üN_20j_ha" index="124"/>
    <alias name="" field="W2C_Out_VJG_üN_30j_ha" index="125"/>
    <alias name="" field="W2C_Out_DFG_Bu_0j_Tfm" index="126"/>
    <alias name="" field="W2C_Out_DFG_Bu_3j_Tfm" index="127"/>
    <alias name="" field="W2C_Out_DFG_Bu_6j_Tfm" index="128"/>
    <alias name="" field="W2C_Out_DFG_Bu_10j_Tfm" index="129"/>
    <alias name="" field="W2C_Out_DFG_Bu_0j_ha" index="130"/>
    <alias name="" field="W2C_Out_DFG_Bu_3j_ha" index="131"/>
    <alias name="" field="W2C_Out_DFG_Bu_6j_ha" index="132"/>
    <alias name="" field="W2C_Out_DFG_Bu_10j_ha" index="133"/>
    <alias name="" field="W2C_Out_VJG_Bu_0j_ha" index="134"/>
    <alias name="" field="W2C_Out_VJG_Bu_10j_ha" index="135"/>
    <alias name="" field="W2C_Out_VJG_Bu_20j_ha" index="136"/>
    <alias name="" field="W2C_Out_VJG_Bu_30j_ha" index="137"/>
    <alias name="" field="W2C_Out_DFG_Ei_0j_Tfm" index="138"/>
    <alias name="" field="W2C_Out_DFG_Ei_3j_Tfm" index="139"/>
    <alias name="" field="W2C_Out_DFG_Ei_6j_Tfm" index="140"/>
    <alias name="" field="W2C_Out_DFG_Ei_10j_Tfm" index="141"/>
    <alias name="" field="W2C_Out_DFG_Ei_0j_ha" index="142"/>
    <alias name="" field="W2C_Out_DFG_Ei_3j_ha" index="143"/>
    <alias name="" field="W2C_Out_DFG_Ei_6j_ha" index="144"/>
    <alias name="" field="W2C_Out_DFG_Ei_10j_ha" index="145"/>
    <alias name="" field="W2C_Out_VJG_Ei_0j_ha" index="146"/>
    <alias name="" field="W2C_Out_VJG_Ei_10j_ha" index="147"/>
    <alias name="" field="W2C_Out_VJG_Ei_20j_ha" index="148"/>
    <alias name="" field="W2C_Out_VJG_Ei_30j_ha" index="149"/>
    <alias name="" field="W2C_Out_DFG_Es_0j_Tfm" index="150"/>
    <alias name="" field="W2C_Out_DFG_Es_3j_Tfm" index="151"/>
    <alias name="" field="W2C_Out_DFG_Es_6j_Tfm" index="152"/>
    <alias name="" field="W2C_Out_DFG_Es_10j_Tfm" index="153"/>
    <alias name="" field="W2C_Out_DFG_Es_0j_ha" index="154"/>
    <alias name="" field="W2C_Out_DFG_Es_3j_ha" index="155"/>
    <alias name="" field="W2C_Out_DFG_Es_6j_ha" index="156"/>
    <alias name="" field="W2C_Out_DFG_Es_10j_ha" index="157"/>
    <alias name="" field="W2C_Out_VJG_Es_0j_ha" index="158"/>
    <alias name="" field="W2C_Out_VJG_Es_10j_ha" index="159"/>
    <alias name="" field="W2C_Out_VJG_Es_20j_ha" index="160"/>
    <alias name="" field="W2C_Out_VJG_Es_30j_ha" index="161"/>
    <alias name="" field="W2C_Out_DFG_Ah_0j_Tfm" index="162"/>
    <alias name="" field="W2C_Out_DFG_Ah_3j_Tfm" index="163"/>
    <alias name="" field="W2C_Out_DFG_Ah_6j_Tfm" index="164"/>
    <alias name="" field="W2C_Out_DFG_Ah_10j_Tfm" index="165"/>
    <alias name="" field="W2C_Out_DFG_Ah_0j_ha" index="166"/>
    <alias name="" field="W2C_Out_DFG_Ah_3j_ha" index="167"/>
    <alias name="" field="W2C_Out_DFG_Ah_6j_ha" index="168"/>
    <alias name="" field="W2C_Out_DFG_Ah_10j_ha" index="169"/>
    <alias name="" field="W2C_Out_VJG_Ah_0j_ha" index="170"/>
    <alias name="" field="W2C_Out_VJG_Ah_10j_ha" index="171"/>
    <alias name="" field="W2C_Out_VJG_Ah_20j_ha" index="172"/>
    <alias name="" field="W2C_Out_VJG_Ah_30j_ha" index="173"/>
    <alias name="" field="W2C_Out_DFG_üL_0j_Tfm" index="174"/>
    <alias name="" field="W2C_Out_DFG_üL_3j_Tfm" index="175"/>
    <alias name="" field="W2C_Out_DFG_üL_6j_Tfm" index="176"/>
    <alias name="" field="W2C_Out_DFG_üL_10j_Tfm" index="177"/>
    <alias name="" field="W2C_Out_DFG_üL_0j_ha" index="178"/>
    <alias name="" field="W2C_Out_DFG_üL_3j_ha" index="179"/>
    <alias name="" field="W2C_Out_DFG_üL_6j_ha" index="180"/>
    <alias name="" field="W2C_Out_DFG_üL_10j_ha" index="181"/>
    <alias name="" field="W2C_Out_VJG_üL_0j_ha" index="182"/>
    <alias name="" field="W2C_Out_VJG_üL_10j_ha" index="183"/>
    <alias name="" field="W2C_Out_VJG_üL_20j_ha" index="184"/>
    <alias name="" field="W2C_Out_VJG_üL_30j_ha" index="185"/>
  </aliases>
  <defaults>
    <default field="area_m2" expression="" applyOnUpdate="0"/>
    <default field="ID" expression="" applyOnUpdate="0"/>
    <default field="hmax" expression="" applyOnUpdate="0"/>
    <default field="hdom" expression="" applyOnUpdate="0"/>
    <default field="dg_ks_coun" expression="" applyOnUpdate="0"/>
    <default field="dg_ks_sum" expression="" applyOnUpdate="0"/>
    <default field="dg_us_coun" expression="" applyOnUpdate="0"/>
    <default field="dg_us_sum" expression="" applyOnUpdate="0"/>
    <default field="dg_ms_coun" expression="" applyOnUpdate="0"/>
    <default field="dg_ms_sum" expression="" applyOnUpdate="0"/>
    <default field="dg_os_coun" expression="" applyOnUpdate="0"/>
    <default field="dg_os_sum" expression="" applyOnUpdate="0"/>
    <default field="dg_ueb_cou" expression="" applyOnUpdate="0"/>
    <default field="dg_ueb_sum" expression="" applyOnUpdate="0"/>
    <default field="dg_count" expression="" applyOnUpdate="0"/>
    <default field="dg_sum" expression="" applyOnUpdate="0"/>
    <default field="DG_ks" expression="" applyOnUpdate="0"/>
    <default field="DG_us" expression="" applyOnUpdate="0"/>
    <default field="DG_ms" expression="" applyOnUpdate="0"/>
    <default field="DG_os" expression="" applyOnUpdate="0"/>
    <default field="DG_ueb" expression="" applyOnUpdate="0"/>
    <default field="DG" expression="" applyOnUpdate="0"/>
    <default field="nh_count" expression="" applyOnUpdate="0"/>
    <default field="nh_sum" expression="" applyOnUpdate="0"/>
    <default field="NH" expression="" applyOnUpdate="0"/>
    <default field="nh_count_1" expression="" applyOnUpdate="0"/>
    <default field="nh_sum_1" expression="" applyOnUpdate="0"/>
    <default field="nhm_count" expression="" applyOnUpdate="0"/>
    <default field="nhm_mean" expression="" applyOnUpdate="0"/>
    <default field="NH_OS" expression="" applyOnUpdate="0"/>
    <default field="NH_OS_PIX" expression="" applyOnUpdate="0"/>
    <default field="nr" expression="" applyOnUpdate="0"/>
    <default field="struktur" expression="" applyOnUpdate="0"/>
    <default field="tbk_typ" expression="" applyOnUpdate="0"/>
    <default field="frehner63" expression="" applyOnUpdate="0"/>
    <default field="WG_WIS2" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_SP" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_ddom_IST" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_hdom_IST" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_Station" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_Age" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_bst_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_letzterEingriff" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_typ" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Fi" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Ta" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Fö" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Lä" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_üN" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Bu" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Ei" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Es" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_Ah" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_MS_üL" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Total_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Total_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Total_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Total_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Total_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fi_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fi_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fi_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fi_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fi_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ta_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ta_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ta_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ta_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ta_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Fö_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fö_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fö_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fö_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Fö_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Lä_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Lä_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Lä_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Lä_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Lä_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üN_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üN_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üN_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üN_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üN_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Bu_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Bu_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Bu_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Bu_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Bu_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ei_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ei_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ei_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ei_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ei_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Es_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Es_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Es_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Es_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Es_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_Ah_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ah_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ah_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ah_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_Ah_30j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_0j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_3j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_6j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_10j_Tfm" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_3j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_6j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_DFG_üL_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üL_0j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üL_10j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üL_20j_ha" expression="" applyOnUpdate="0"/>
    <default field="W2C_Out_VJG_üL_30j_ha" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="area_m2" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="ID" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="hmax" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="hdom" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ks_coun" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ks_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_us_coun" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_us_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ms_coun" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ms_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_os_coun" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_os_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ueb_cou" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_ueb_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_count" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="dg_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG_ks" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG_us" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG_ms" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG_os" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG_ueb" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="DG" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nh_count" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nh_sum" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="NH" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nh_count_1" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nh_sum_1" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nhm_count" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nhm_mean" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="NH_OS" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="NH_OS_PIX" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="nr" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="struktur" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="tbk_typ" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="frehner63" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="WG_WIS2" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_SP" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_ddom_IST" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_hdom_IST" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_Station" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_Age" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_bst_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_letzterEingriff" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_typ" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Fi" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Ta" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Fö" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Lä" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_üN" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Bu" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Ei" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Es" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_Ah" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_MS_üL" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Total_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Total_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Total_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Total_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Total_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fi_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fi_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fi_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fi_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fi_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ta_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ta_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ta_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ta_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ta_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Fö_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fö_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fö_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fö_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Fö_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Lä_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Lä_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Lä_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Lä_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Lä_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üN_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üN_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üN_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üN_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üN_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Bu_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Bu_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Bu_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Bu_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Bu_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ei_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ei_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ei_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ei_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ei_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Es_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Es_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Es_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Es_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Es_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_Ah_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ah_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ah_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ah_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_Ah_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_0j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_3j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_6j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_10j_Tfm" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_3j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_6j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_DFG_üL_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üL_0j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üL_10j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üL_20j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint field="W2C_Out_VJG_üL_30j_ha" constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="area_m2" desc="" exp=""/>
    <constraint field="ID" desc="" exp=""/>
    <constraint field="hmax" desc="" exp=""/>
    <constraint field="hdom" desc="" exp=""/>
    <constraint field="dg_ks_coun" desc="" exp=""/>
    <constraint field="dg_ks_sum" desc="" exp=""/>
    <constraint field="dg_us_coun" desc="" exp=""/>
    <constraint field="dg_us_sum" desc="" exp=""/>
    <constraint field="dg_ms_coun" desc="" exp=""/>
    <constraint field="dg_ms_sum" desc="" exp=""/>
    <constraint field="dg_os_coun" desc="" exp=""/>
    <constraint field="dg_os_sum" desc="" exp=""/>
    <constraint field="dg_ueb_cou" desc="" exp=""/>
    <constraint field="dg_ueb_sum" desc="" exp=""/>
    <constraint field="dg_count" desc="" exp=""/>
    <constraint field="dg_sum" desc="" exp=""/>
    <constraint field="DG_ks" desc="" exp=""/>
    <constraint field="DG_us" desc="" exp=""/>
    <constraint field="DG_ms" desc="" exp=""/>
    <constraint field="DG_os" desc="" exp=""/>
    <constraint field="DG_ueb" desc="" exp=""/>
    <constraint field="DG" desc="" exp=""/>
    <constraint field="nh_count" desc="" exp=""/>
    <constraint field="nh_sum" desc="" exp=""/>
    <constraint field="NH" desc="" exp=""/>
    <constraint field="nh_count_1" desc="" exp=""/>
    <constraint field="nh_sum_1" desc="" exp=""/>
    <constraint field="nhm_count" desc="" exp=""/>
    <constraint field="nhm_mean" desc="" exp=""/>
    <constraint field="NH_OS" desc="" exp=""/>
    <constraint field="NH_OS_PIX" desc="" exp=""/>
    <constraint field="nr" desc="" exp=""/>
    <constraint field="struktur" desc="" exp=""/>
    <constraint field="tbk_typ" desc="" exp=""/>
    <constraint field="frehner63" desc="" exp=""/>
    <constraint field="WG_WIS2" desc="" exp=""/>
    <constraint field="W2C_Out_SP" desc="" exp=""/>
    <constraint field="W2C_Out_ddom_IST" desc="" exp=""/>
    <constraint field="W2C_Out_hdom_IST" desc="" exp=""/>
    <constraint field="W2C_Out_Station" desc="" exp=""/>
    <constraint field="W2C_Out_Age" desc="" exp=""/>
    <constraint field="W2C_Out_bst_ha" desc="" exp=""/>
    <constraint field="W2C_Out_letzterEingriff" desc="" exp=""/>
    <constraint field="W2C_Out_MS_typ" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Fi" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Ta" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Fö" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Lä" desc="" exp=""/>
    <constraint field="W2C_Out_MS_üN" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Bu" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Ei" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Es" desc="" exp=""/>
    <constraint field="W2C_Out_MS_Ah" desc="" exp=""/>
    <constraint field="W2C_Out_MS_üL" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Total_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Total_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Total_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Total_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Total_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fi_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fi_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fi_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fi_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fi_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ta_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ta_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ta_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ta_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ta_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Fö_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fö_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fö_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fö_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Fö_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Lä_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Lä_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Lä_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Lä_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Lä_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üN_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üN_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üN_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üN_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üN_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Bu_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Bu_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Bu_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Bu_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Bu_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ei_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ei_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ei_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ei_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ei_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Es_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Es_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Es_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Es_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Es_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_Ah_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ah_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ah_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ah_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_Ah_30j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_0j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_3j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_6j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_10j_Tfm" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_3j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_6j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_DFG_üL_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üL_0j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üL_10j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üL_20j_ha" desc="" exp=""/>
    <constraint field="W2C_Out_VJG_üL_30j_ha" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" sortOrder="0" actionWidgetStyle="dropDown">
    <columns>
      <column name="ID" type="field" hidden="0" width="-1"/>
      <column name="hmax" type="field" hidden="0" width="-1"/>
      <column name="hdom" type="field" hidden="0" width="-1"/>
      <column name="area_m2" type="field" hidden="0" width="-1"/>
      <column name="DG_ks" type="field" hidden="0" width="-1"/>
      <column name="DG_us" type="field" hidden="0" width="-1"/>
      <column name="DG_ms" type="field" hidden="0" width="-1"/>
      <column name="DG_os" type="field" hidden="0" width="-1"/>
      <column name="DG_ueb" type="field" hidden="0" width="-1"/>
      <column name="DG" type="field" hidden="0" width="-1"/>
      <column name="nr" type="field" hidden="0" width="-1"/>
      <column name="struktur" type="field" hidden="0" width="-1"/>
      <column name="tbk_typ" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
      <column name="dg_ks_coun" type="field" hidden="0" width="-1"/>
      <column name="dg_ks_sum" type="field" hidden="0" width="-1"/>
      <column name="dg_us_coun" type="field" hidden="0" width="-1"/>
      <column name="dg_us_sum" type="field" hidden="0" width="-1"/>
      <column name="dg_ms_coun" type="field" hidden="0" width="-1"/>
      <column name="dg_ms_sum" type="field" hidden="0" width="-1"/>
      <column name="dg_os_coun" type="field" hidden="0" width="-1"/>
      <column name="dg_os_sum" type="field" hidden="0" width="-1"/>
      <column name="dg_ueb_cou" type="field" hidden="0" width="-1"/>
      <column name="dg_ueb_sum" type="field" hidden="0" width="-1"/>
      <column name="dg_count" type="field" hidden="0" width="-1"/>
      <column name="dg_sum" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_SP" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_ddom_IST" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_hdom_IST" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_Station" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_Age" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_bst_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_letzterEingriff" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_typ" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Fi" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Ta" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Bu" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Ei" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Es" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Ah" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Total_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Total_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Total_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Total_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Total_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fi_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fi_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fi_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fi_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fi_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ta_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ta_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ta_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ta_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ta_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Bu_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Bu_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Bu_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Bu_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Bu_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ei_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ei_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ei_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ei_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ei_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Es_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Es_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Es_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Es_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Es_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Ah_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ah_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ah_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ah_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Ah_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="nh_count" type="field" hidden="0" width="-1"/>
      <column name="nh_sum" type="field" hidden="0" width="-1"/>
      <column name="NH" type="field" hidden="0" width="-1"/>
      <column name="nh_count_1" type="field" hidden="0" width="-1"/>
      <column name="nh_sum_1" type="field" hidden="0" width="-1"/>
      <column name="nhm_count" type="field" hidden="0" width="-1"/>
      <column name="nhm_mean" type="field" hidden="0" width="-1"/>
      <column name="NH_OS" type="field" hidden="0" width="-1"/>
      <column name="NH_OS_PIX" type="field" hidden="0" width="-1"/>
      <column name="frehner63" type="field" hidden="0" width="-1"/>
      <column name="WG_WIS2" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Fö" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_Lä" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_üN" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_MS_üL" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Fö_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fö_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fö_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fö_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Fö_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_Lä_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Lä_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Lä_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Lä_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_Lä_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üN_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üN_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üN_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üN_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üN_30j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_0j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_3j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_6j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_10j_Tfm" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_3j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_6j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_DFG_üL_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üL_0j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üL_10j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üL_20j_ha" type="field" hidden="0" width="-1"/>
      <column name="W2C_Out_VJG_üL_30j_ha" type="field" hidden="0" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="DG" editable="1"/>
    <field name="DGRed" editable="1"/>
    <field name="DGUe90_mea" editable="1"/>
    <field name="DG_ks" editable="1"/>
    <field name="DG_ms" editable="1"/>
    <field name="DG_os" editable="1"/>
    <field name="DG_ueb" editable="1"/>
    <field name="DG_us" editable="1"/>
    <field name="ID" editable="1"/>
    <field name="NH" editable="1"/>
    <field name="NH_OS" editable="1"/>
    <field name="NH_OS_PIX" editable="1"/>
    <field name="PrFi_mean" editable="1"/>
    <field name="PrFo_mean" editable="1"/>
    <field name="PrLa_mean" editable="1"/>
    <field name="PrTa_mean" editable="1"/>
    <field name="V_mean" editable="1"/>
    <field name="W2C_Out_Age" editable="0"/>
    <field name="W2C_Out_DFG_Ah_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ah_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ah_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ah_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ah_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ah_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ah_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ah_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Bu_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Bu_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Bu_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Bu_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Bu_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Bu_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Bu_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Bu_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ei_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ei_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ei_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ei_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ei_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ei_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ei_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ei_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Es_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Es_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Es_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Es_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Es_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Es_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Es_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Es_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fi_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fi_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fi_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fi_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fi_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fi_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fi_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fi_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Foe_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Foe_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Foe_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Foe_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Foe_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Foe_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Foe_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Foe_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fö_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fö_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fö_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fö_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fö_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fö_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Fö_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Fö_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lae_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lae_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lae_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lae_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lae_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lae_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lae_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lae_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lä_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lä_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lä_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lä_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lä_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lä_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Lä_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Lä_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ta_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ta_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ta_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ta_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ta_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ta_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Ta_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Ta_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Total_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Total_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Total_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Total_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Total_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Total_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_Total_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_Total_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueL_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueL_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueL_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueL_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueL_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueL_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueL_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueL_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueN_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueN_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueN_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueN_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueN_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueN_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_ueN_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_ueN_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üL_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üL_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üL_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üL_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üL_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üL_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üL_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üL_6j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üN_0j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üN_0j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üN_10j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üN_10j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üN_3j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üN_3j_ha" editable="0"/>
    <field name="W2C_Out_DFG_üN_6j_Tfm" editable="0"/>
    <field name="W2C_Out_DFG_üN_6j_ha" editable="0"/>
    <field name="W2C_Out_MS_Ah" editable="0"/>
    <field name="W2C_Out_MS_Bu" editable="0"/>
    <field name="W2C_Out_MS_Ei" editable="0"/>
    <field name="W2C_Out_MS_Es" editable="0"/>
    <field name="W2C_Out_MS_Fi" editable="0"/>
    <field name="W2C_Out_MS_Foe" editable="0"/>
    <field name="W2C_Out_MS_Fö" editable="0"/>
    <field name="W2C_Out_MS_Lae" editable="0"/>
    <field name="W2C_Out_MS_Lä" editable="0"/>
    <field name="W2C_Out_MS_Ta" editable="0"/>
    <field name="W2C_Out_MS_typ" editable="0"/>
    <field name="W2C_Out_MS_ueL" editable="0"/>
    <field name="W2C_Out_MS_ueN" editable="0"/>
    <field name="W2C_Out_MS_üL" editable="0"/>
    <field name="W2C_Out_MS_üN" editable="0"/>
    <field name="W2C_Out_SP" editable="0"/>
    <field name="W2C_Out_Station" editable="0"/>
    <field name="W2C_Out_VJG_Ah_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ah_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ah_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ah_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Bu_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Bu_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Bu_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Bu_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ei_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ei_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ei_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ei_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Es_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Es_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Es_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Es_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fi_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fi_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fi_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fi_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Foe_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Foe_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Foe_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Foe_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fö_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fö_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fö_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Fö_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lae_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lae_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lae_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lae_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lä_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lä_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lä_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Lä_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ta_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ta_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ta_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Ta_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Total_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Total_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Total_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_Total_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueL_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueL_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueL_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueL_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueN_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueN_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueN_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_ueN_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üL_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üL_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üL_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üL_30j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üN_0j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üN_10j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üN_20j_ha" editable="0"/>
    <field name="W2C_Out_VJG_üN_30j_ha" editable="0"/>
    <field name="W2C_Out_bst_ha" editable="0"/>
    <field name="W2C_Out_ddom_IST" editable="0"/>
    <field name="W2C_Out_hdom_IST" editable="0"/>
    <field name="W2C_Out_letzterEingriff" editable="0"/>
    <field name="WG_WIS2" editable="1"/>
    <field name="area_m2" editable="1"/>
    <field name="dg_count" editable="1"/>
    <field name="dg_ks_coun" editable="1"/>
    <field name="dg_ks_sum" editable="1"/>
    <field name="dg_ms_coun" editable="1"/>
    <field name="dg_ms_sum" editable="1"/>
    <field name="dg_os_coun" editable="1"/>
    <field name="dg_os_sum" editable="1"/>
    <field name="dg_sum" editable="1"/>
    <field name="dg_ueb_cou" editable="1"/>
    <field name="dg_ueb_sum" editable="1"/>
    <field name="dg_us_coun" editable="1"/>
    <field name="dg_us_sum" editable="1"/>
    <field name="frehner63" editable="1"/>
    <field name="hdom" editable="1"/>
    <field name="hmax" editable="1"/>
    <field name="nh_count" editable="1"/>
    <field name="nh_count_1" editable="1"/>
    <field name="nh_sum" editable="1"/>
    <field name="nh_sum_1" editable="1"/>
    <field name="nhm_count" editable="1"/>
    <field name="nhm_mean" editable="1"/>
    <field name="nr" editable="1"/>
    <field name="struktur" editable="1"/>
    <field name="tbk_typ" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="DG" labelOnTop="0"/>
    <field name="DGRed" labelOnTop="0"/>
    <field name="DGUe90_mea" labelOnTop="0"/>
    <field name="DG_ks" labelOnTop="0"/>
    <field name="DG_ms" labelOnTop="0"/>
    <field name="DG_os" labelOnTop="0"/>
    <field name="DG_ueb" labelOnTop="0"/>
    <field name="DG_us" labelOnTop="0"/>
    <field name="ID" labelOnTop="0"/>
    <field name="NH" labelOnTop="0"/>
    <field name="NH_OS" labelOnTop="0"/>
    <field name="NH_OS_PIX" labelOnTop="0"/>
    <field name="PrFi_mean" labelOnTop="0"/>
    <field name="PrFo_mean" labelOnTop="0"/>
    <field name="PrLa_mean" labelOnTop="0"/>
    <field name="PrTa_mean" labelOnTop="0"/>
    <field name="V_mean" labelOnTop="0"/>
    <field name="W2C_Out_Age" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ah_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Bu_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ei_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Es_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fi_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Foe_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Fö_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lae_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Lä_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Ta_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_Total_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueL_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_ueN_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üL_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_0j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_10j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_3j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_3j_ha" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_6j_Tfm" labelOnTop="0"/>
    <field name="W2C_Out_DFG_üN_6j_ha" labelOnTop="0"/>
    <field name="W2C_Out_MS_Ah" labelOnTop="0"/>
    <field name="W2C_Out_MS_Bu" labelOnTop="0"/>
    <field name="W2C_Out_MS_Ei" labelOnTop="0"/>
    <field name="W2C_Out_MS_Es" labelOnTop="0"/>
    <field name="W2C_Out_MS_Fi" labelOnTop="0"/>
    <field name="W2C_Out_MS_Foe" labelOnTop="0"/>
    <field name="W2C_Out_MS_Fö" labelOnTop="0"/>
    <field name="W2C_Out_MS_Lae" labelOnTop="0"/>
    <field name="W2C_Out_MS_Lä" labelOnTop="0"/>
    <field name="W2C_Out_MS_Ta" labelOnTop="0"/>
    <field name="W2C_Out_MS_typ" labelOnTop="0"/>
    <field name="W2C_Out_MS_ueL" labelOnTop="0"/>
    <field name="W2C_Out_MS_ueN" labelOnTop="0"/>
    <field name="W2C_Out_MS_üL" labelOnTop="0"/>
    <field name="W2C_Out_MS_üN" labelOnTop="0"/>
    <field name="W2C_Out_SP" labelOnTop="0"/>
    <field name="W2C_Out_Station" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ah_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ah_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ah_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ah_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Bu_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Bu_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Bu_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Bu_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ei_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ei_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ei_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ei_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Es_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Es_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Es_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Es_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fi_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fi_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fi_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fi_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Foe_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Foe_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Foe_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Foe_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fö_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fö_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fö_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Fö_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lae_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lae_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lae_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lae_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lä_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lä_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lä_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Lä_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ta_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ta_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ta_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Ta_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Total_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Total_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Total_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_Total_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueL_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueL_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueL_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueL_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueN_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueN_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueN_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_ueN_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üL_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üL_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üL_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üL_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üN_0j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üN_10j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üN_20j_ha" labelOnTop="0"/>
    <field name="W2C_Out_VJG_üN_30j_ha" labelOnTop="0"/>
    <field name="W2C_Out_bst_ha" labelOnTop="0"/>
    <field name="W2C_Out_ddom_IST" labelOnTop="0"/>
    <field name="W2C_Out_hdom_IST" labelOnTop="0"/>
    <field name="W2C_Out_letzterEingriff" labelOnTop="0"/>
    <field name="WG_WIS2" labelOnTop="0"/>
    <field name="area_m2" labelOnTop="0"/>
    <field name="dg_count" labelOnTop="0"/>
    <field name="dg_ks_coun" labelOnTop="0"/>
    <field name="dg_ks_sum" labelOnTop="0"/>
    <field name="dg_ms_coun" labelOnTop="0"/>
    <field name="dg_ms_sum" labelOnTop="0"/>
    <field name="dg_os_coun" labelOnTop="0"/>
    <field name="dg_os_sum" labelOnTop="0"/>
    <field name="dg_sum" labelOnTop="0"/>
    <field name="dg_ueb_cou" labelOnTop="0"/>
    <field name="dg_ueb_sum" labelOnTop="0"/>
    <field name="dg_us_coun" labelOnTop="0"/>
    <field name="dg_us_sum" labelOnTop="0"/>
    <field name="frehner63" labelOnTop="0"/>
    <field name="hdom" labelOnTop="0"/>
    <field name="hmax" labelOnTop="0"/>
    <field name="nh_count" labelOnTop="0"/>
    <field name="nh_count_1" labelOnTop="0"/>
    <field name="nh_sum" labelOnTop="0"/>
    <field name="nh_sum_1" labelOnTop="0"/>
    <field name="nhm_count" labelOnTop="0"/>
    <field name="nhm_mean" labelOnTop="0"/>
    <field name="nr" labelOnTop="0"/>
    <field name="struktur" labelOnTop="0"/>
    <field name="tbk_typ" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"ID"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
