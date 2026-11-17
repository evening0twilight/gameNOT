extends SceneTree
func _initialize() -> void:
	var evidence: Dictionary={}
	for locale: String in ["zh_CN","zh_TW","en"]:
		var path: String="res://data/localization/"+locale+".json"
		if not FileAccess.file_exists(path):printerr("Missing packaged locale "+locale);quit(1);return
		var raw: String=FileAccess.get_file_as_string(path)
		var data: Variant=JSON.parse_string(raw)
		if not data is Dictionary:quit(1);return
		evidence[locale]={"entries":data.size(),"sha256":raw.sha256_text()}
	var i18n=load("res://scripts/presentation/localization.gd")
	for locale: String in i18n.LOCALES:
		i18n.locale=locale
		evidence[locale].title=i18n.t("ui.ea0219b09f08")
	print("PACKAGED_LANGUAGES: "+JSON.stringify(evidence))
	quit(0)
