# coding=UTF-8
import os
import re
import zipfile
import codecs

#translate
import argparse
from google.cloud import translate
import six

#常數
TARGET_LANG = "zh-TW"
SOURCE_LANG = "en"
EXCEPT_MODS = [
  "MicsLocale",
  "mod-list.json",
  "mod-settings.json"
]

mods_path = os.path.realpath(os.path.realpath(__file__) + "/../../..")
my_locale_path = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../locale/" + TARGET_LANG)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+ "/credentials.json")

def main():
  os.chdir(mods_path)
  mod_locales_pair = getModsLocaleFiles()
  
  # 準備資料夾
  os.chdir(my_locale_path)
  if not os.path.exists(my_locale_path):
    os.makedirs(my_locale_path)
    
   #開始翻譯
  translate_client = translate.Client()
  regex_translate_strs = re.compile(r"^([^#=]+)=(.*)$")
  regex_mod_name = re.compile(r"(^([\w\s\-])+)_\d+\.\d+\.\d+")
  # { mod : { config_name : config_content,.. }, ..}
  for mod in mod_locales_pair:
    mod_name = regex_mod_name.match(mod).group(1)
    configs = mod_locales_pair[mod]
    for config in configs:
      text_file_str = mod + " - " + config + ".cfg"
      if os.path.exists(text_file_str):
        print("已有同模組同版本檔案, 自動略過. (" + text_file_str + ")")
        continue
      regex_old_file_name = re.compile("^" + re.escape(mod_name) + r"(_\d+\.\d+\.\d+)? - " + re.escape(config) + r"\.cfg")
      if list(filter(regex_old_file_name.match, os.listdir(my_locale_path))):
        print("已有同模組檔案, 可能須手動檢查是否有缺漏, 自動略過. (" + text_file_str + ")")
        continue
      init_string = configs[config].decode("utf8")
      final_string = init_string;
      for line in init_string.splitlines():
        m = regex_translate_strs.match(line)
        if(m):
          source = m.group(2).replace("\\n", "@@%%@@")
          translated = translate_client.translate(source, target_language=TARGET_LANG).get("translatedText")
          # translated = source
          final_string = final_string.replace(m.group(0), "# " + m.group(2) + "\n" + m.group(1) + "=" + translated)
      text_file = codecs.open(text_file_str, mode="w", encoding="utf8")
      text_file.write(final_string)
      text_file.close()
      print("檔案翻譯完成: " + text_file_str)
      #print(final_string)
          
      
  
def getModsLocaleFiles():
  mod_locales_pair = {}
  regex_locale_source = re.compile(r"([\w\s\-]+_\d+\.\d+\.\d+)\/locale\/" + re.escape(SOURCE_LANG) + "\/([\w\s\-]+)\.cfg")
  regex_locale_target = re.compile(r"([\w\s\-]+_\d+\.\d+\.\d+)\/locale\/" + re.escape(TARGET_LANG) + "\/([\w\s\-]+)\.cfg")
  for mod in os.listdir(mods_path):
    # 過濾自己本身以及列表檔案
    if any(except_mod in mod for except_mod in EXCEPT_MODS):
      continue
    # 過濾自己本身以及列表檔案
    if mod.endswith(".zip"):
      zip = zipfile.ZipFile(mod, 'r')
      
      # 掃描來源語言檔案
      for name in zip.namelist():
        m = regex_locale_source.match(name)
        if not m: #如果沒有語言檔
          continue
        file_path = m.group(0)
        mod_name = m.group(1)
        config_name = m.group(2)
        config_content = zip.open(file_path, 'r').read()
        locales = {}
        if mod_name in mod_locales_pair.keys():
          locales = mod_locales_pair[mod_name]
          locales[config_name] = config_content
        else:
          locales[config_name] = config_content
        mod_locales_pair[mod_name] = locales
      
      # 檢查是否已有目標語系
      for name in zip.namelist():
        m = regex_locale_target.match(name)
        if not m: #如果沒有語言檔
          continue
        file_path = m.group(0)
        mod_name = m.group(1)
        if mod_name in mod_locales_pair:
          del mod_locales_pair[mod_name]
    else:
      print("目前不支援 zip 以外的模組或這個檔案並非模組 (檔名: " + mod + ")")
      # TODO 資料夾型態
  return mod_locales_pair
        
if __name__ == '__main__':
  main()
  