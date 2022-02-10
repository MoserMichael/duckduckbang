#!/usr/bin/env python3
import argparse
import traceback
import sys
import pathlib
import io
import html5lib
import psutil
import comm

def install_selenium_driver():
    return ""


#def last_effort_selenium_download(url, browser, selenium_driver = None):
#    from selenium_firefox import Firefox
#
#    browser = Firefox()
#    driver.get(url)
#    driver.find_element_by_xpath("/html")
#    print(driver.page_source)
#    driver.close()


def _kill_it(name):
    for ps_info in psutil.process_iter(['name', 'status']):
        if ps_info.name == name and ps_info.status == psutil.STATUS_RUNNING:
            if comm.Global.trace_on:
                print(f"killing pid {ps_info.pid}")
            proc = psutil.Process(ps_info.pid)
            proc.terminate()


def last_effort_selenium_download(url, browser, selenium_driver = None, kill_browser_proc = True):
    from selenium import webdriver

    if comm.Global.trace_on:
        print(f"Selenium_download url: {url} browser: {browser}.")

    if browser is None or browser == "" or browser == "firefox":
        if selenium_driver is None:
            # check if current dir has selenium driver
            path = pathlib.Path("geckodriver")
            if path.is_file():
                selenium_driver = "./geckodriver"
            else:
                selenium_driver = install_selenium_driver()

        if comm.Global.trace_on:
            print(f"gecko driver: {selenium_driver}")
        driver = webdriver.Firefox(executable_path=selenium_driver)

    elif browser == "chrome":
        # didn't check this out really. should work, if the driver is present.
        driver = webdriver.Chrome(selenium_driver) #options)

    else:
        raise ValueError(f"invalid value. browser: {browser}")

    has_error = False
    try:
        driver.get(url)

    except Exception as ex:
        if comm.Global.trace_on:
            print(f"Error while loading url: {url} error: {ex}")
            traceback.print_exception(*sys.exc_info())

        has_error = True
        rval = f"load_error: {ex}"

    #driver.find_element_by_xpath("/html")
    if not has_error:
        rval = driver.page_source

    if comm.Global.trace_on:
        print(f"trace: {rval}")

    driver.close()
    driver.quit()

    if kill_browser_proc:
        # currently there seems to be a bug in the firefox selenium driver.
        # the firefox window is not closed, despite calling both close and quit.
        # now killing the firefox process, as a last resort.
        if browser == "firefox":
            _kill_it("firefox")

    if has_error:
        raise ValueError(rval)
    return rval

class SeleniumSoup:
    def __init__(self, browser = None, selenium_driver = None):
        self.browser = browser
        self.selenium_driver = selenium_driver

    def get_soup(self, url):
        text  = last_effort_selenium_download("https://" + url, browser = self.browser, selenium_driver = self.selenium_driver)
        data_file = io.StringIO(text)
        return html5lib.parse(data_file, treebuilder="etree") #lxml")


def _parse_cmd_line():
    usage = """
Use selenium library to automate the browser at downloading a given url.
print the text of the html files.
This is a last effort to download a url,
as some content delivery networks,like cloudfare and medium make the task difficult.
An equivalent scanner would have to evaluate javascript as part of the process,
The whole thing has become quite complex and tricky, in other words.
Automating a real browser is kind of a last effort, in this respect.
"""

    parse = argparse.ArgumentParser(
        description=usage, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    group = parse.add_argument_group("actions")

    group.add_argument(
        "--url",
        "-u",
        type=str,
        dest="url",
        help="fetch this url and show the downloaded html text"
    )

    group.add_argument(
        "--browser",
        "-b",
        default="",
        type=str,
        dest="browser",
        help="specify browser (firefox|chrome) default: firefox"
    )



    group.add_argument(
        "--verbose",
        "-v",
        default=False,
        action="store_true",
        dest="verbose",
        help="verbose debug output"
    )

    group.add_argument(
        "--debug",
        "-d",
        default=False,
        action="store_true",
        dest="debug",
        help="show content of downloaded page"
    )


    return parse.parse_args()



def _run_cmd():
    cmd = _parse_cmd_line()

    if cmd.verbose:
        comm.Global.trace_on = True

    if cmd.debug:
        comm.Global.debug_on = True

    if cmd.url is not None:
        try:
            text = last_effort_selenium_download(cmd.url, cmd.browser)
            print(text)
        except Exception as exc:
            print(f"Error: {exc}")

if __name__ == '__main__':
    _run_cmd()
