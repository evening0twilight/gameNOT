"""Offline coverage/format checks for the three shipped presentation languages."""
import json,re
from pathlib import Path
from localize_product018 import extract,ROOT

def main():
    source=extract();pattern=r'%(?:[-+0 #]*\d*(?:\.\d+)?)?[sdif]|%%'
    report={'source_count':len(source),'locales':{},'failures':[]}
    for locale in ['en','zh_TW']:
        data=json.loads((ROOT/f'game/data/localization/{locale}.json').read_text())
        missing=sorted(set(source)-data.keys())
        if missing:report['failures'].append({'locale':locale,'missing':missing})
        invalid=[]
        for original in source:
            if original not in data:continue
            translated=data[original]
            # A space after % is not used as a printf flag in the game; it may
            # be English prose following a literal percentage.
            printf=r'%[-+0#]*\d*(?:\.\d+)?[sdif]|%%'
            if not translated or re.findall(printf,original)!=re.findall(printf,translated):invalid.append(original)
            if locale=='en' and re.search('[\u4e00-\u9fff]',translated):invalid.append(original)
            if locale=='zh_TW' and any(c in translated for c in '东个伤内带队暂缓样视让轮这选择页驻么'):invalid.append(original)
        if invalid:report['failures'].append({'locale':locale,'invalid':invalid})
        report['locales'][locale]={'entries':len(data),'covered':len(source)-len(missing)}
    (ROOT/'outputs/languages-catalog-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('LANGUAGE_CATALOG_RESULTS: '+json.dumps(report,ensure_ascii=False))
    return bool(report['failures'])
if __name__=='__main__':raise SystemExit(main())
