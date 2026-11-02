"""Selenium exercises: labs 1-5 are prepared; write your own code in lab6().

Only the Python standard library and Selenium are needed. All application
requests go to an ephemeral HTTP server bound to 127.0.0.1.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import platform
import sys
import threading
import time
import traceback
import uuid
from collections import Counter
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import selenium
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select, WebDriverWait
except ImportError:
    print('Selenium is missing. Run: python -m pip install -r requirements.txt')
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent
LAB_NAMES = {
    1: 'Browser and locators',
    2: 'Form interactions and assertions',
    3: 'Immediate lookup vs explicit wait',
    4: 'Observe red / green / refactor',
    5: 'Boundary regression from CSV',
    6: 'เขียนโค้ดเอง: แก้ชื่อแล้วลงทะเบียนใหม่',
}
PREPARED_LABS = (1, 2, 3, 4, 5)


class ComparisonFailure(AssertionError):
    def __init__(self, expected, actual):
        self.expected, self.actual = expected, actual
        super().__init__(f'expected={expected!r}; actual={actual!r}')


class EarlyLookupFailure(AssertionError):
    """Only raised for the intentionally early lookup in lab 3."""


def compare(expected, actual):
    # Equivalent to assert actual == expected, with structured report details.
    if actual != expected:
        raise ComparisonFailure(expected, actual)
    return {'expected': expected, 'actual': actual}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            # Browsers may cancel speculative/local requests on navigation or
            # quit. Only client disconnections are quiet; other errors surface.
            pass


class LabRunner:
    def __init__(self, driver, base_url, pace):
        self.driver, self.base_url, self.pace = driver, base_url, pace
        self.rows = []
        self.batch_rows = []
        self.folder = None

    def page(self, version='fixed'):
        # Reload before every scenario: form fields and JS state are reset.
        self.driver.get(f'{self.base_url}/index.html?version={version}')
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'heading')))

    def pause(self):
        # Presentation pacing only; synchronization always uses explicit waits.
        time.sleep(self.pace)

    def case(self, lab, name, fn, expected_failure=None):
        started = time.perf_counter()
        row = {'lab': lab, 'case': name, 'expected': '', 'actual': ''}
        try:
            details = fn() or {}
            row.update(details)
            row['status'] = 'XPASS' if expected_failure else 'PASS'
            row['detail'] = ('The planned failure did not occur. Investigate this run.'
                             if expected_failure else 'Observed behavior matches the test.')
        except NotImplementedError as exc:
            row['status'] = 'TODO'
            row['detail'] = str(exc)
        except Exception as exc:
            row['expected'] = getattr(exc, 'expected', '')
            row['actual'] = getattr(exc, 'actual', '')
            intentional = expected_failure is not None and expected_failure(exc)
            row['status'] = ('EXPECTED_FAIL' if intentional else
                             'FAIL' if isinstance(exc, AssertionError) else 'ERROR')
            row['detail'] = f'{type(exc).__name__}: {exc}'
            trace_name = f'{len(self.batch_rows)+1:02d}_{name}_trace.txt'
            (self.folder / trace_name).write_text(traceback.format_exc(), encoding='utf-8')
            row['trace'] = trace_name
        row['seconds'] = round(time.perf_counter() - started, 3)
        image_name = f'{len(self.batch_rows)+1:02d}_{name}.png'
        try:
            if not self.driver.save_screenshot(str(self.folder / image_name)):
                raise RuntimeError('WebDriver returned false when saving screenshot')
            row['screenshot'] = image_name
        except Exception as exc:
            row['status'] = 'ERROR'
            row['detail'] += f'; screenshot could not be saved: {exc}'
        self.batch_rows.append(row)
        self.rows.append(row)
        print(f"[{row['status']}] L{lab} {name} | {row['detail']}", flush=True)
        if row['expected'] != '' or row['actual'] != '':
            print(f"  expected={row['expected']!r}; actual={row['actual']!r}", flush=True)
        self.pause()

    def lab1(self):
        def title():
            self.page()
            return compare('CE Course Registration', self.driver.title)
        self.case(1, 'page_title', title)
        locators = [
            ('by_id', By.ID, 'student-name', 'input'),
            ('by_name', By.NAME, 'student_name', 'input'),
            ('by_css', By.CSS_SELECTOR, '[data-testid="register"]', 'button'),
            ('by_xpath', By.XPATH, '//h1[@id="heading"]', 'h1'),
        ]
        for name, by, value, expected_tag in locators:
            def find(by=by, value=value, expected_tag=expected_tag):
                self.page()
                element = self.driver.find_element(by, value)
                self.driver.execute_script(
                    "arguments[0].style.outline='4px solid #e48e16'", element)
                return compare(expected_tag, element.tag_name)
            self.case(1, name, find)

    def submit(self, name='CE Student', credits=3, consent=True, version='fixed'):
        self.page(version)
        self.driver.find_element(By.NAME, 'student_name').send_keys(name)
        Select(self.driver.find_element(By.ID, 'course')).select_by_value('selenium')
        credit_box = self.driver.find_element(By.ID, 'credits')
        credit_box.clear()
        credit_box.send_keys(str(credits))
        if consent:
            self.driver.find_element(By.ID, 'consent').click()
        self.pause()
        self.driver.find_element(By.CSS_SELECTOR, '[data-testid="register"]').click()
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element(By.ID, 'result').get_attribute('data-code') != 'READY')
        result = self.driver.find_element(By.ID, 'result')
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center',behavior:'instant'})", result)
        return result.get_attribute('data-code')

    def lab2(self):
        self.case(2, 'valid_form', lambda: compare('REGISTERED', self.submit()))
        self.case(2, 'blank_name', lambda: compare('NAME_REQUIRED', self.submit(name='')))
        self.case(2, 'missing_consent', lambda: compare(
            'CONSENT_REQUIRED', self.submit(consent=False)))

    def lab3(self):
        def immediate():
            self.page()
            self.driver.find_element(By.ID, 'load-course').click()
            # No pause and no wait before this lookup.
            try:
                actual = self.driver.find_element(By.ID, 'course-ready').text
            except NoSuchElementException as exc:
                raise EarlyLookupFailure(
                    'The course-ready element is not in the DOM yet (NoSuchElementException).') from exc
            return compare('COURSE_READY', actual)

        self.case(3, 'immediate_lookup', immediate,
                  expected_failure=lambda exc: isinstance(exc, EarlyLookupFailure))

        def waited():
            self.page()
            self.driver.find_element(By.ID, 'load-course').click()
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'course-ready')))
            return compare('COURSE_READY', element.text)

        self.case(3, 'explicit_wait', waited)

    def lab4(self):
        # Identical functional test, three prebuilt application versions.
        for version in ('buggy', 'fixed', 'refactored'):
            def reject_four(version=version):
                return compare('CREDITS_OUT_OF_RANGE', self.submit(credits=4, version=version))
            expected = None
            if version == 'buggy':
                expected = lambda exc: (
                    isinstance(exc, ComparisonFailure)
                    and exc.expected == 'CREDITS_OUT_OF_RANGE'
                    and exc.actual == 'REGISTERED')
            self.case(4, f'credits_4_{version}', reject_four, expected_failure=expected)

    def lab5(self):
        with (ROOT / 'test_cases.csv').open(encoding='utf-8', newline='') as source:
            cases = list(csv.DictReader(source))
        for data in cases:
            def check(data=data):
                return compare(data['expected'], self.submit(credits=int(data['credits'])))
            self.case(5, data['case_id'], check)

    def lab6(self):
        # LAB 6: ฝึกเขียนโค้ดเอง — แก้ชื่อแล้วลงทะเบียนใหม่ 
        # โจทย์: เขียน Selenium ทดสอบ 2 รอบต่อไปนี้บนหน้าเว็บเดียวกัน
        # 1. กรอกชื่อเป็นช่องว่าง 3 ตัว เลือก Software Testing (ค่า testing)
        #    ใช้ 3 หน่วยกิต ติ๊กยืนยัน แล้วกด Register
        #    ตรวจว่า data-code ของผลลัพธ์เป็น NAME_REQUIRED
        # 2. ล้างช่องชื่อแล้วกรอก CE Student จากนั้นกด Register อีกครั้ง
        #    ตรวจว่า data-code เปลี่ยนเป็น REGISTERED
        # เงื่อนไข: ไม่เปิดหน้าใหม่ ไม่ refresh และไม่ติ๊กยืนยันซ้ำในรอบที่ 2
        # ใช้ explicit wait รอผลใหม่ และ assert หรือ compare() ตรวจผลทั้ง 2 รอบ
        # คำถามหลังทำ: ทำไมชื่อเป็นช่องว่างจึงไม่ผ่าน แต่ CE Student ผ่าน?
        # ดูตัวอย่างคำสั่งจาก submit() และ lab3() ได้ แต่ห้ามเรียก submit()
        # เพราะ submit() เปิดหน้าใหม่ทุกครั้ง
        # Locator: student-name, course, credits, consent, submit, result (ใช้ By.ID)
        # อ่านรหัสผลด้วย get_attribute('data-code'); ช่องหน่วยกิตมีค่า 3 อยู่แล้ว
        # วิธีทำ: เติมโค้ดในช่อง TODO ด้านล่าง บันทึกไฟล์ แล้วเลือกเมนู 6
        # โปรแกรมเปิดเว็บ สร้างรายงาน และปิด browser ให้ ไม่ต้องเปิด server เอง
        def check():
            self.page('fixed')
            driver = self.driver
            wait = WebDriverWait(driver, 10)

            # TODO: เขียนโค้ดของนักศึกษาตรงนี้ แล้วลบบรรทัด raise ด้านล่าง
            raise NotImplementedError('ยังไม่ได้ทำ Lab 6: เติมโค้ดใน lab6() แล้วรันเมนู 6 อีกครั้ง')

        self.case(6, 'correct_name_on_same_form', check)

    def execute(self, labs, check=False):
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
        self.folder = ROOT / 'reports' / stamp
        self.folder.mkdir(parents=True)
        self.batch_rows = []
        try:
            if check:
                def smoke():
                    self.page()
                    return compare('CE Course Registration', self.driver.title)
                self.case(0, 'environment_check', smoke)
            else:
                for lab in labs:
                    print(f'\n--- LAB {lab}: {LAB_NAMES[lab]} ---', flush=True)
                    getattr(self, f'lab{lab}')()
        except Exception as exc:
            # Input/file errors outside a test must never produce a green report.
            self.batch_rows.append({'lab': 0, 'case': 'runner_error', 'status': 'ERROR',
                                    'detail': str(exc), 'expected': '', 'actual': ''})
            (self.folder / 'runner_trace.txt').write_text(traceback.format_exc(), encoding='utf-8')
        self.write_report()
        return not any(row['status'] in ('FAIL', 'ERROR', 'XPASS', 'TODO') for row in self.batch_rows)

    def write_report(self):
        counts = dict(Counter(row['status'] for row in self.batch_rows))
        metadata = {'created': datetime.now().astimezone().isoformat(),
                    'python': platform.python_version(), 'platform': platform.platform(),
                    'selenium': selenium.__version__,
                    'browser': self.driver.capabilities.get('browserName'),
                    'browser_version': self.driver.capabilities.get('browserVersion'),
                    'counts': counts, 'results': self.batch_rows}
        (self.folder / 'results.json').write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        e = lambda value: html.escape(str(value))
        rows = []
        for row in self.batch_rows:
            assets = []
            if row.get('screenshot'):
                assets.append(f'<a href="{e(row["screenshot"])}">Screenshot</a>')
            if row.get('trace'):
                assets.append(f'<a href="{e(row["trace"])}">Traceback</a>')
            rows.append(f'<tr><td>{e(row["lab"])}</td><td>{e(row["case"])}</td>'
                        f'<td class="{e(row["status"])}">{e(row["status"])}</td>'
                        f'<td>{e(row["expected"])}</td><td>{e(row["actual"])}</td>'
                        f'<td>{e(row["detail"])}</td><td>{" / ".join(assets)}</td></tr>')
        report = '''<!doctype html><html lang="th"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Selenium Lab Report</title>
<style>body{font:16px/1.6 Tahoma,system-ui,sans-serif;color:#18304b;margin:30px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bdcbd9;padding:9px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#e9eff8}.PASS{color:#126549}.EXPECTED_FAIL,.TODO{color:#805800}.FAIL,.ERROR,.XPASS{color:#af1733}a{color:#145cc5}code{background:#eef3fa}</style>
<h1>Selenium Python / ผลการทดลอง</h1>
<p>PASS = ตรงตามคาด; EXPECTED_FAIL = ความล้มเหลวที่เตรียมไว้ให้เรียนรู้;
FAIL / ERROR / XPASS = ต้องตรวจสอบผลรอบนี้</p>
<p>Lab 3: EXPECTED_FAIL เป็นปัญหาจังหวะการค้นหา; Lab 4: EXPECTED_FAIL แสดงบั๊กของแอปจริง</p>
<p>Expected/actual ว่างใน Lab 3 หมายถึงเกิด exception ก่อนเปรียบเทียบค่า</p>
<p>TODO = ยังไม่ได้เติมโค้ด Lab 6 ให้เปิด run_labs.py แล้วเขียนโค้ดใน lab6()</p>
<p>เปิด screenshot และ traceback เพื่อประกอบคำตอบ บันทึกคำตอบในใบงานแยกต่างหาก</p>
'''
        report += f'<p>{e(metadata["created"])} | {e(metadata["browser"])} {e(metadata["browser_version"])} | Selenium {e(metadata["selenium"])}</p>'
        report += f'<p><strong>{e(counts)}</strong></p><table><tr><th>Lab</th><th>Case</th><th>Status</th><th>Expected</th><th>Actual</th><th>Detail</th><th>Evidence</th></tr>'
        report += ''.join(rows) + '</table></html>'
        (self.folder / 'report.html').write_text(report, encoding='utf-8')
        print('\nSummary:', counts, flush=True)
        print('Report:', self.folder / 'report.html', flush=True)


def make_driver(args):
    options = webdriver.ChromeOptions() if args.browser == 'chrome' else webdriver.EdgeOptions()
    if args.headless:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1200,950')
    options.add_argument('--no-first-run')
    if args.binary:
        options.binary_location = str(Path(args.binary).resolve())
    kwargs = {'options': options}
    if args.driver:
        service_type = ChromeService if args.browser == 'chrome' else EdgeService
        kwargs['service'] = service_type(executable_path=str(Path(args.driver).resolve()))
    driver_type = webdriver.Chrome if args.browser == 'chrome' else webdriver.Edge
    driver = driver_type(**kwargs)
    driver.implicitly_wait(0)
    driver.set_page_load_timeout(20)
    return driver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', choices=['1', '2', '3', '4', '5', '6', 'all'],
                        help='Choose lab 1-6; all runs prepared labs 1-5')
    parser.add_argument('--check', action='store_true', help='Check browser and local server before class')
    parser.add_argument('--browser', choices=['chrome', 'edge'], default='chrome')
    parser.add_argument('--headless', action='store_true', help='For instructor verification only')
    parser.add_argument('--driver', help='Optional preinstalled driver executable for offline rooms')
    parser.add_argument('--binary', help='Optional path to a browser executable')
    parser.add_argument('--pace', type=float, default=1.0, help='Observation pause in seconds (0-5)')
    args = parser.parse_args()
    if not 0 <= args.pace <= 5:
        parser.error('--pace must be from 0 to 5 seconds')
    if args.check and args.lab:
        parser.error('Choose --check or --lab, not both')

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'web')))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    driver = None
    ok = True
    try:
        print('Starting browser... First use may download a matching driver.', flush=True)
        driver = make_driver(args)
        runner = LabRunner(driver, f'http://127.0.0.1:{server.server_port}', args.pace)
        print('Web application:', runner.base_url, flush=True)
        print('Do not close or click inside the automated browser while a lab is running.', flush=True)
        if args.check:
            ok = runner.execute([], check=True)
        elif args.lab:
            selected = list(PREPARED_LABS) if args.lab == 'all' else [int(args.lab)]
            ok = runner.execute(selected)
        else:
            while True:
                print('\nChoose a lab (1-5: prepared; 6: write code in lab6()):')
                for number, name in LAB_NAMES.items():
                    print(f'  {number}. {name}')
                print('  7. Run prepared labs (1-5)\n  0. Exit')
                try:
                    choice = input('Lab number: ').strip()
                except EOFError:
                    break
                if choice == '0':
                    break
                if choice not in ('1', '2', '3', '4', '5', '6', '7'):
                    print('Please enter 0-7.')
                    continue
                selected = list(PREPARED_LABS) if choice == '7' else [int(choice)]
                ok = runner.execute(selected) and ok
    except KeyboardInterrupt:
        print('\nStopped by user.')
        ok = False
    except Exception as exc:
        print(f'\nENVIRONMENT ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
        print('See README.md: check Python, browser, network, and driver compatibility.', file=sys.stderr)
        ok = False
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
