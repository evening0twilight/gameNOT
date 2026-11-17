extends RefCounted
## UI-only language resources. Never translate or mutate authoritative campaign data.
const LOCALES=["zh_CN","zh_TW","en"]
const NAMES={"zh_CN":"简体中文","zh_TW":"繁體中文","en":"English"}
static var locale: String="zh_CN"
static var font_size: int=20
static var messages: Dictionary={}
static var catalogs: Dictionary={}
static var missing: Dictionary={}
static var templates: Dictionary={}
static var rendered: Dictionary={}
static var depth: int=0
static func initialize() -> void:
	messages=JSON.parse_string(FileAccess.get_file_as_string("res://data/localization/zh_CN.json"))
	var config:=ConfigFile.new()
	if config.load("user://ui_preferences.cfg")==OK:
		locale=str(config.get_value("ui","locale","zh_CN"));font_size=int(config.get_value("ui","font_size",20))
	if locale not in LOCALES and locale!="en_XA":locale="zh_CN"
	if font_size not in [16,20,24]:font_size=20
	TranslationServer.set_locale(locale)
static func s(source: String) -> String:
	if locale=="zh_CN" or source.is_empty():return source
	if locale=="en_XA":
		return source if source.begins_with("［") else "［"+source+"·".repeat(maxi(1,ceili(source.length()*.3)))+"］"
	if not catalogs.has(locale):
		var path: String="res://data/localization/"+locale+".json"
		catalogs[locale]=JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else {}
	var catalog: Dictionary=catalogs[locale]
	if catalog.has(source):return catalog[source]
	if rendered.get(locale,{}).has(source):return rendered[locale][source]
	if source.contains(" "):
		var prefix: String=source.get_slice(" ",0)
		if not prefix.is_empty() and catalog.has(prefix):return catalog[prefix]+s(source.substr(prefix.length()))
	if depth<3:
		var formatted: String=formatted_source(source,catalog)
		if not formatted.is_empty():return formatted
	for separator: String in ["\n"," · ","：",": "," / ","、"," → "]:
		if not source.contains(separator):continue
		var parts: PackedStringArray=source.split(separator,true,1)
		for i: int in range(parts.size()):parts[i]=s(parts[i])
		return (": " if locale=="en" and separator=="：" else separator).join(parts)
	return source
static func t(key: String) -> String:
	if messages.is_empty():messages=JSON.parse_string(FileAccess.get_file_as_string("res://data/localization/zh_CN.json"))
	return s(str(messages.get(key,"⟦"+key+"⟧")))
static func content(domain: String,id: String,field: String,fallback: String) -> String:
	var key: String="content."+domain+"."+id+"."+field
	return t(key) if messages.has(key) else s(fallback)
static func save_preferences() -> void:
	var config:=ConfigFile.new();config.set_value("ui","locale",locale);config.set_value("ui","font_size",font_size);config.save("user://ui_preferences.cfg")
	TranslationServer.set_locale(locale)

# Domain messages retain their original values in saves. Match their authored
# printf template only at the presentation boundary, before translating arguments.
static func formatted_source(source: String,catalog: Dictionary) -> String:
	var chinese: bool=false
	for index: int in range(source.length()):
		if source.unicode_at(index)>=0x4e00 and source.unicode_at(index)<=0x9fff:chinese=true;break
	if not chinese:return ""
	if not templates.has(locale):
		templates[locale]=[]
		var placeholders:=RegEx.new();placeholders.compile("%[-+0#]*[0-9]*(?:\\.[0-9]+)?[sdif]")
		for original: String in catalog:
			var matches: Array[RegExMatch]=placeholders.search_all(original)
			if matches.is_empty():continue
			var pattern: String="^";var offset: int=0;var formats: Array=[]
			for match_result: RegExMatch in matches:
				pattern+=regex_literal(original.substr(offset,match_result.get_start()-offset))
				var format: String=match_result.get_string();formats.append(format.right(1))
				pattern+="(.+?)" if format.ends_with("s") else "([+-]?[0-9]+(?:\\.[0-9]+)?)"
				offset=match_result.get_end()
			pattern+=regex_literal(original.substr(offset))+"$"
			var regex:=RegEx.new()
			if regex.compile(pattern)==OK:templates[locale].append({"regex":regex,"text":catalog[original],"formats":formats})
	for template: Dictionary in templates[locale]:
		var found: RegExMatch=template.regex.search(source)
		if found==null:continue
		var values: Array=[];depth+=1
		for index: int in range(template.formats.size()):
			var value: String=found.get_string(index+1)
			values.append(s(value) if template.formats[index]=="s" else (float(value) if template.formats[index]=="f" else int(value)))
		depth-=1
		var result: String=template.text%values
		if not rendered.has(locale):rendered[locale]={}
		rendered[locale][source]=result
		return result
	return ""
static func regex_literal(value: String) -> String:
	var result: String=""
	for character: String in value:
		if character in "\\.^$*+?()[]{}|":result+="\\"
		result+=character
	return result
