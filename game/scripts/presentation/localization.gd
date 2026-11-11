extends RefCounted
## Presentation-only localization. Locale preferences never enter campaign saves.
static var locale: String="zh_CN"
static var font_size: int=20
static var messages: Dictionary={}
static var translation: Translation
static func initialize() -> void:
	messages=JSON.parse_string(FileAccess.get_file_as_string("res://data/localization/zh_CN.json"))
	var config:=ConfigFile.new()
	if config.load("user://ui_preferences.cfg")==OK:
		locale=str(config.get_value("ui","locale","zh_CN"))
		font_size=int(config.get_value("ui","font_size",20))
	if locale not in ["zh_CN","en_XA"]:locale="zh_CN"
	if font_size not in [16,20,24]:font_size=20
	TranslationServer.set_locale(locale)
	if translation!=null:TranslationServer.remove_translation(translation)
	translation=Translation.new()
	translation.locale="zh_CN"
	for key: String in messages:translation.add_message(key,messages[key])
	TranslationServer.add_translation(translation)
static func t(key: String) -> String:
	if messages.is_empty():messages=JSON.parse_string(FileAccess.get_file_as_string("res://data/localization/zh_CN.json"))
	var source: String=str(messages.get(key,"⟦"+key+"⟧"))
	if locale=="en_XA":return "［"+source+"·".repeat(maxi(1,ceili(source.length()*0.3)))+"］"
	var translated: String=TranslationServer.translate(key)
	return source if translated==key else translated
static func content(domain: String,id: String,field: String,fallback: String) -> String:
	var key: String="content."+domain+"."+id+"."+field
	return t(key) if messages.has(key) else fallback
static func save_preferences() -> void:
	var config:=ConfigFile.new()
	config.set_value("ui","locale",locale)
	config.set_value("ui","font_size",font_size)
	config.save("user://ui_preferences.cfg")
	TranslationServer.set_locale(locale)
