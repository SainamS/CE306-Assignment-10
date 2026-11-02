# Selenium Python สำหรับ ป.ตรี วิศวกรรมคอมพิวเตอร์

นักศึกษาเลือกเมนูเพื่อรันแล็บ แล้วใช้สิ่งที่เห็นบนเบราว์เซอร์และรายงานตอบคำถามในใบงาน ทุกแล็บมีโค้ดให้พร้อม จึงไม่ต้องเขียนหรือแก้โปรแกรม

## แล็บในชุดนี้

1. เปิดเบราว์เซอร์และค้นหาองค์ประกอบด้วย locator
2. กรอกฟอร์มและตรวจผลด้วย assertion
3. เปรียบเทียบการค้นหาทันทีกับ explicit wait
4. ใช้ test เดิมตรวจเว็บเวอร์ชัน buggy, fixed และ refactored
5. ทดสอบค่าขอบเขตด้วยข้อมูลจาก CSV

## เริ่มจากไฟล์ใด

- `student_lab.html`: ใบงานภาษาไทย พิมพ์แจกหรือกรอกคำตอบแล้วดาวน์โหลดได้
- `instructor_guide.html`: คำแนะนำสำหรับผู้สอน เฉลย และเกณฑ์คะแนน
- `run_labs.py`: โปรแกรมเมนูแล็บ 1-5
- `web/index.html`: เว็บจำลองลงทะเบียนเรียน มีเวอร์ชัน buggy / fixed / refactored
- `test_cases.csv`: ข้อมูลทดสอบค่าขอบเขตที่ใช้ใน Lab 5
- `requirements.txt`: Selenium รุ่นที่ใช้ตรวจสอบชุดนี้
- `VERIFICATION.md`: บันทึกการตรวจสอบของผู้จัดทำ
- `example_report/report.html`: รายงานตัวอย่างสำหรับดูรูปแบบผลทดสอบ นักศึกษาต้องสร้างรายงานของตนเอง
- `SETUP_WINDOWS.cmd` / `START_LABS.cmd`: ใช้เตรียมเครื่องก่อนเรียนและเปิดเมนูแล็บตามลำดับ

แตก ZIP ลงโฟลเดอร์ที่เขียนไฟล์ได้ แล้วรันแล็บจากโฟลเดอร์ที่แตกไฟล์แล้ว

## เตรียมเครื่องก่อนเรียน

ติดตั้ง Python 3.10 ขึ้นไป และ Google Chrome หรือ Microsoft Edge รุ่นปัจจุบัน แนะนำ Python 3.11 ขึ้นไป
การเตรียมเครื่องครั้งแรกต้องใช้อินเทอร์เน็ตเพื่อดาวน์โหลดแพ็กเกจและ driver
ชุดแล็บไม่ต้องใช้ Java, Django, pytest, Selenium Grid หรือบัญชีเว็บไซต์

Windows: เปิด Terminal ในโฟลเดอร์ชุดแล็บ แล้วรันตามบรรทัด:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_labs.py --check
.\.venv\Scripts\python.exe run_labs.py --lab all --headless --pace 0
```

หากไม่มีคำสั่ง `py` ให้ใช้ `python` ในบรรทัดแรก ต้องเป็น Python 3.10+
คำสั่งเรียก Python ใน virtual environment โดยตรง จึงไม่ต้อง activate และไม่ติดข้อจำกัด PowerShell execution policy
ขั้น `--check` ควรได้ `PASS: 1` และ all ควรได้ `PASS: 16, EXPECTED_FAIL: 2`
ตรวจในแต่ละเครื่อง/บัญชีผู้ใช้ที่จะใช้เรียน เพราะ driver cache อาจต่างกัน

macOS / Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_labs.py --check
.venv/bin/python run_labs.py --lab all --headless --pace 0
```

หากใช้ Edge ให้ต่อท้าย `--browser edge` ในทุกคำสั่งที่เรียก `run_labs.py`
ผลการตรวจบน Windows ด้วย Chrome และ Edge อยู่ใน VERIFICATION.md หากใช้ระบบอื่น ให้รัน preflight ก่อนสอน

## นักศึกษาเริ่มเรียน

เปิด `student_lab.html` ด้วยเบราว์เซอร์ปกติ แล้วเปิด Terminal ในโฟลเดอร์แล็บ:

```powershell
.\.venv\Scripts\python.exe run_labs.py
```

เลือกหมายเลข 1-5 ตามใบงาน ใช้ 0 เพื่อจบ โปรแกรมเปิดเว็บและปิดเว็บให้เอง
บน Windows สามารถดับเบิลคลิก `START_LABS.cmd` แทนคำสั่งข้างต้นได้
ตอนโปรแกรมกำลังรัน ห้ามคลิกหรือปิดหน้าต่างเบราว์เซอร์ที่ Selenium ควบคุม
รอให้กลับมาที่เมนูก่อนเปิดรายงานในเบราว์เซอร์ปกติอีกหน้าต่างหนึ่ง
ไม่ต้องใช้ `rtk` และไม่ต้องติดตั้งส่วนเสริมใดสำหรับนักศึกษา

หากใช้เมนูไม่ได้ ให้รันทีละแล็บด้วยตัวเลือก `--lab 1` ถึง `--lab 5`
แต่ละกรณีเปิดหน้าเว็บใหม่ จึงรันซ้ำหรือข้ามลำดับได้

## รายงานและการส่งงาน

แต่ละการรันสร้าง `reports/<วันเวลา_รหัส>/report.html`, `results.json`, ภาพ PNG ของแต่ละกรณี
และ traceback เมื่อเกิดข้อผิดพลาด เปิด `report.html` จากพาธที่ Terminal แจ้ง
โฟลเดอร์รายงานรอบใหม่ไม่ทับรอบเก่า ส่งคำตอบจากใบงานพร้อมโฟลเดอร์รายงานของแล็บ 1-5
ใบงานมีปุ่มดาวน์โหลดคำตอบเป็น TXT หรือใช้ Print / Save as PDF ของเบราว์เซอร์
การดาวน์โหลดคำตอบต้องทำก่อนปิดหรือ reload ใบงาน คำตอบไม่ได้บันทึกอัตโนมัติ

สถานะ:

- `PASS`: ผลจริงตรงกับผลที่คาด รวมกรณีกรอกข้อมูลผิดแล้วระบบปฏิเสธถูกต้อง
- `EXPECTED_FAIL`: ความล้มเหลวที่เตรียมให้สังเกต เฉพาะ L3 immediate_lookup และ L4 credits_4_buggy
- `FAIL`: ผลจริงผิดจากผลที่คาดในกรณีอื่น
- `ERROR`: ปัญหาแวดล้อม/locator/ไฟล์/driver หรือข้อผิดพลาดที่ไม่ใช่ assertion
- `XPASS`: กรณีที่เตรียมไว้ให้ล้มเหลวกลับผ่าน ให้ผู้สอนตรวจรายละเอียดของรอบนั้น

เมื่อผลตรงตามที่ชุดแล็บกำหนด โปรแกรมจะคืน exit code 0 รวมกรณี EXPECTED_FAIL ที่เตรียมไว้
FAIL / ERROR / XPASS คืน 1; กรณีไม่มี Selenium คืน 2
Lab 4 มี assertion ที่ล้มเหลวจริง ตรวจ expected และ actual ได้ในรายงานและ traceback
ป้าย EXPECTED_FAIL ใช้ระบุความล้มเหลวที่นำมาสอน บั๊กของแอปใน Lab 4 ยังเป็นพฤติกรรมที่ผิดข้อกำหนด

## ห้องที่อินเทอร์เน็ตจำกัด

เว็บแล็บใช้ HTTP ที่ 127.0.0.1 ส่วน Selenium Manager อาจยังเช็กหรือดาวน์โหลด driver เมื่อสร้าง session
ก่อนใช้ในห้องที่ไม่มีอินเทอร์เน็ต ให้ผู้ดูแลเตรียม browser และ driver ที่ตรงรุ่น แล้วระบุพาธเอง:

```powershell
.\.venv\Scripts\python.exe run_labs.py --driver "C:\lab-tools\chromedriver.exe"
```

Edge ใช้ `--browser edge --driver "C:\lab-tools\msedgedriver.exe"`
ใช้ `--binary "พาธไฟล์ browser"` ได้เมื่อ browser อยู่ตำแหน่งพิเศษ
ดาวน์โหลด driver จากผู้ผลิตตามลิงก์ในคู่มืออาจารย์ และทดสอบแบบตัดอินเทอร์เน็ตจริงก่อนคาบ
สำหรับเครื่องที่ยังไม่มีแพ็กเกจ ผู้ดูแลเตรียม wheel ล่วงหน้าบนระบบและ Python รุ่นเดียวกัน:

```powershell
.\.venv\Scripts\python.exe -m pip download -r requirements.txt -d wheels
.\.venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r requirements.txt
```

ZIP นี้ไม่ได้รวม Python, browser, driver หรือ wheels และไม่ได้ทดสอบ offline ในเครื่องผู้จัดทำ

## แก้ปัญหาเบื้องต้น

| อาการ | การดำเนินการ |
|---|---|
| `No module named selenium` | ใช้ Python ใน `.venv` และติดตั้ง requirements ด้วย Python ตัวเดียวกัน |
| เปิด driver ไม่ได้ / `SessionNotCreatedException` | ตรวจ browser กับ driver ให้ตรงรุ่น รัน `--check` ใหม่; ตรวจ proxy/สิทธิ์ดาวน์โหลด |
| หา Chrome ไม่เจอ | ลอง `--browser edge` หรือให้ผู้ดูแลติดตั้ง Chrome |
| ไม่เห็น browser | อย่าใช้ `--headless` ในกิจกรรมนักศึกษา |
| เว็บหรือช่องกรอกหายระหว่างรัน | อย่าคลิก/ปิด browser ที่ถูกควบคุม รันแล็บเดิมซ้ำ |
| `XPASS` ใน Lab 3 | อาจเป็นจังหวะเครื่องช้าจนข้อมูลปรากฏก่อน lookup รันซ้ำและรายงานให้อาจารย์ทราบ |
| `TimeoutException` หรือ `ERROR` อื่น | เปิด traceback; แยกจาก EXPECTED_FAIL ที่เตรียมไว้ ให้ผู้สอนตรวจสอบ |
| รายงานเขียนไม่ได้ | แตก ZIP ลงโฟลเดอร์ที่ผู้ใช้เขียนได้และอย่าเปิดจาก ZIP |

`--pace 2` หรือ `--pace 3` ช่วยให้เห็นการสาธิตนานขึ้น เป็นการหน่วงเพื่อสังเกตเท่านั้น
การรอความพร้อมของเว็บใน Lab 3 ใช้ explicit wait และไม่ได้อาศัย pace

## แนวคิดและแหล่งอ้างอิง

กิจกรรม โค้ด และเว็บจำลองเขียนขึ้นใหม่ โดยใช้แนวคิดจากหนังสือต่อไปนี้ ไม่ได้คัดลอกบทฝึกหัดหรือข้อความในหนังสือ:

1. Boni García, *Hands-On Selenium WebDriver with Java* (2022), บท 3 WebDriver Fundamentals
   (locators, interactions, waiting strategies), บท 4 Screenshots และบท 8 Failure Analysis
   โดยแปลงแนวคิดมาใช้ Python ไม่ต้องติดตั้ง Java
2. Harry J. W. Percival, *Test-Driven Development with Python*, ไฟล์ที่แนบมี Preface to the Third Edition;
   บท 2 functional test / unittest, บท 4 user interactions / test behaviour / refactoring,
   และบท 13 explicit wait helper ใช้เป็นแนวคิดประกอบ ไม่ได้ใช้แอป Django ของหนังสือ

เอกสารหลักที่ตรวจ API เมื่อ 23 ตุลาคม 2026:

- https://www.selenium.dev/documentation/webdriver/getting_started/first_script/
- https://www.selenium.dev/documentation/webdriver/elements/locators/
- https://www.selenium.dev/documentation/webdriver/waits/
- https://www.selenium.dev/documentation/selenium_manager/
- https://pypi.org/project/selenium/4.51.0/
- https://developer.chrome.com/docs/chromedriver/downloads
- https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

ขอบเขต: เป็น functional test ผ่าน browser ของเว็บจำลองฝั่งหน้าเว็บ ไม่มีฐานข้อมูล
จึงไม่ครอบคลุม E2E ของระบบ backend จริง ความปลอดภัย ประสิทธิภาพ หรือทุกกรณีของการลงทะเบียน
Lab 4 ให้สังเกต Red-Green-Refactor จากเวอร์ชันสำเร็จรูป การฝึก TDD ให้ครบกระบวนการยังต้องให้นักศึกษาเขียน test และแก้โปรแกรมด้วยตนเอง
