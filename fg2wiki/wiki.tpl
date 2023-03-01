{%-set outputstate = namespace(spellcasting=false, spells=false) -%}
{%- macro spellcasting_if_not_yet() -%}
{%if not outputstate.spellcasting %}
==Spellcasting==
{% set outputstate.spellcasting = true -%}
{%- endif -%}
{%- endmacro -%}
{%- macro spells_if_not_yet() -%}
{%if not outputstate.spells %}
===Spells===
{% set outputstate.spells = true -%}
{%- endif -%}
{%- endmacro -%}
[[File:{{ charname | replace(' ', '') }}.png |150px]]
{%- set classes = character.classes|only_tag_children|list-%}
[[{{ charname }}]] - {{ character.race | xmlc }} Level {{ classes | map(attribute="level") | map("xmlc")|sum}} ({{ classes | formatclasslevels}})
{% if character.background -%}
* Background: {{character.background | xmlc}}
{%- endif -%}
{% if character.personalitytraits is not none -%}
{%- set traitsfull = character.personalitytraits | xmlc -%}
===Traits===
{% for trait in traitsfull.split('\\n') -%}
* {{ trait | nw }}
{% endfor %}
{% endif -%}
{% if character.ideals is not none -%}
{%- set idealsfull = character.ideals | xmlc -%}
===Ideals===
{% for ideal in idealsfull.split('\\n') -%}
* {{ ideal | nw}}
{% endfor %}
{% endif -%}
{% if character.bonds is not none -%}
{%- set bondsfull = character.bonds | xmlc -%}
===Bonds===
{% for bond in bondsfull.split('\\n') -%}
* {{ bond | nw}}
{% endfor %}
{% endif -%}
{% if character.flaws is not none -%}
{%- set flawsfull = character.flaws | xmlc -%}
===Flaws===
{% for flaw in flawsfull.split('\\n') -%}
* {{ flaw | nw}}
{% endfor %}
{% endif -%}
{%  if character.appearance is not none -%}
===Appearance===
{% set appearance = character.appearance | xmlc -%}
{{ appearance.replace('\\n', '\n') | nw}}
{% endif -%}
==Attributes==
{{  '{{col-begin}}' }}
{{  '{{col-break}}' }}
{|class="wikitable"
!Attribute !! Value !! Bonus !! Save
{% for aname in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] -%}
    {% set curabil = character.abilities.find(aname, recursive=false) -%}
|-
| {{ aname | title }} || {{ curabil.score | xmlc }} || {{ curabil.bonus | xmlc(format_with="{:+}") }} || {{ curabil.save | xmlc(format_with="{:+}") }}
{%- endfor %}
|}
{{ '{{col-break}}' }}

===Secondary Attributes===
{|
|Hit Points || ''' {{ character.hp.total | xmlc }}'''
|-
|Armor Class || {{ character.defenses.ac.total | xmlc }}
|-
|Proficiency Bonus || {{ character.profbonus | xmlc(format_with="{:+}") }}
|-
|Passive Perception || {{ character.perception | xmlc }}
|-
|Initiative || {{ character.initiative.total | xmlc(format_with="{:+}") }}
|-
|Base Speed || {{ character.speed.total | xmlc }} Feet
|}
{{ '{{col-end}}' }}

==Skills & Abilities==

{{ '{{col-begin}}' }}
{{ '{{col-break}}' }}
{|class="sortable mw-collapsible wikitable"
!|Skill||Ability||Score
{% for skill in character.skilllist | only_tag_children -%}
{% set prof = skill.prof | xmlc %}
|-
|{% if prof == 1 -%}''{%- endif %}{{ skill.find('name', recursive=false) | xmlc }}{% if prof == 1 -%}''{%- endif %} || {%  if skill.stat %}{{ skill.stat | xmlc | title }}{%  else %}(no stat){% endif %} || {{ skill.total | xmlc(format_with="{:+}") }}
{%- endfor %}
|}

{{ '{{col-break}}' }}

==Languages==

{% if character.languagelist -%}
{% for language in character.languagelist | only_tag_children -%}
* {{ language.find('name', recursive=False) | xmlc }}
{% endfor -%}
{%- endif -%}
{% if character.featurelist is not none%}
==Features==

{% for feature in character.featurelist | only_tag_children -%}
*{{ feature | child_by_tag('name') | xmlc | nw}}
{# feature | child_by_tag('text') | xmlc | trim #}
{%- endfor -%}
{% endif -%}
{{ '{{col-end}}' }}

{% if character.powermeta -%}
{%- set pactslots = character.powermeta | only_prefix_children('pactmagicslots') | map('child_by_tag', 'max') | map('xmlc') | list-%}
{%- if (pactslots | max) > 0 -%}
{{ spellcasting_if_not_yet() }}
===Pact Magic Slots===
{% for slotmax in pactslots %}
{%- if slotmax > 0 -%}
    * Level {{ loop.index }}: {{ slotmax }} {{ slotmax | pluraltext('slot', 'slots')}}
{% endif %}
{%- endfor -%}
{% endif -%}
{%- set spellslots = character.powermeta | only_prefix_children('spellslots') | map('child_by_tag', 'max') | map('xmlc') | list -%}
{%- if (spellslots | max) > 0 -%}
{{ spellcasting_if_not_yet() }}
===Other Slots===
{% for slotmax in spellslots %}
{%- if slotmax > 0 -%}
    * Level {{ loop.index }}: {{ slotmax }} {{ slotmax | pluraltext('slot', 'slots')}}
{% endif %}
{%- endfor -%}
{% endif -%}
{%- if character.powergroup is not none %}
{%- set spellpowersindex = character.powergroup | makepowergroupindex(spellsonly=true) -%}
{% for group, powers in character.powers | only_tag_children | grouptagsby("group") -%}
{% if group in spellpowersindex -%}
{{ spells_if_not_yet() }}
===={{ group }}====
{% for level, powers_for_level in powers | grouptagsby("level")%}
{%- set powers_for_level_list = powers_for_level | list -%}
    * {{ 'Cantrips ' if level == 0 else ('Level %s ' | format(level)) }}({{ powers_for_level_list | count }} known): {{ powers_for_level_list | map('child_by_tag', 'name') | map('xmlc') | join(', ') | nw }}
{% endfor -%}
{% endif -%}
{% endfor -%}
{%- endif -%}
{%- endif -%}

{% if character.inventorylist -%}
==Gear==

{{ character.inventorylist | only_tag_children | map('child_by_tag', 'name') | map('xmlc') | join(', ') }}
{%-endif %}
[[Category:PC Character Sheets]]
