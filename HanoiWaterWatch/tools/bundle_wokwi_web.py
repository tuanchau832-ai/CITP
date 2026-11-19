"""Flatten PlatformIO sources into a Wokwi web sketch; credentials stay ignored."""
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path);args=p.parse_args()
    dest=ROOT/'firmware/wokwi-web';dest.mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'firmware/src').rglob('*'):
        if source.suffix not in ('.h','.cpp'):continue
        name='sketch.ino' if source.name=='main.cpp' else source.name
        text=(source.read_text(encoding='utf-8').replace('"generated/registry.h"','"registry.h"')
              .replace('"../include/config.h"','"config.h"')
              .replace('"../include/config.example.h"','"config.example.h"'))
        (dest/name).write_text(text,encoding='utf-8')
    for name in ('diagram.json',):(dest/name).write_bytes((ROOT/'firmware'/name).read_bytes())
    (dest/'config.example.h').write_bytes((ROOT/'firmware/include/config.example.h').read_bytes())
    if args.config:(dest/'config.h').write_bytes(args.config.read_bytes())
    elif not (dest/'config.h').exists():(dest/'config.h').write_bytes((ROOT/'firmware/include/config.example.h').read_bytes())
    (dest/'libraries.txt').write_text('OneWire\nDallasTemperature\nArduinoJson\nAdafruit SSD1306\nAdafruit GFX Library\n',encoding='utf-8')
    print('Created firmware/wokwi-web; configure the demo key, host and root CA before upload.')
if __name__=='__main__':main()
