# package modules


import concurrent as Concurrent
import ddgs as DuckDuckGoSearch
import json as JSON
import math as Math
import selenium.webdriver as WebDriver
import selenium.webdriver.chrome.options as Options
import selenium.webdriver.common.by as By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as UI
import selenium_stealth as Stealth
import time as Time
import youtube_transcript_api as YouTubeTranscriptApi


import modules.core.file.Operation as Operation
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path
import modules.string.Strings as Strings


__errorsJS = []
__errorsBlocked = []


def loadConfiguration():
    global __errorsJS, __errorsBlocked
    webConfig = Operation.readFile(Path.CONFIGS_WEB_FILE_NAME, None, False)
    if webConfig is not None:
        j = JSON.loads(webConfig)
        __errorsJS = j.get("js_errors")
        __errorsBlocked = j.get("web_errors")
    return


####################
""" BEGIN SEARCH """
####################


def getSearchResultsTextAsync(hrefs, maxSentences):
    TypeCheck.enforce(hrefs, Types.LIST)
    TypeCheck.enforce(maxSentences, Types.INTEGER)

    searchResults = {}
    Util.printDebug("Target links: ")
    for href in hrefs:
        Util.printDebug("   - " + href)

    with Concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for href in hrefs:
            futures.append(executor.submit(getSourceText, websiteIn=href, bypassLength=False, maxSentences=maxSentences))
        for future in Concurrent.futures.as_completed(futures):
            try:
                res = future.result()
            except Exception as e:
                Util.printError("Failed to fetch a source." + str(e))
                res = None
            if res is not None and not Util.checkEmptyString(res[2]):
                searchResults[res[0]] = res[2]
    if len(searchResults.keys()) == 0:
        Util.printError("No sources were compiled.")
    return searchResults


def getSearchResults(keywords, maxSources):
    TypeCheck.enforce(keywords, Types.STRING)
    TypeCheck.enforce(maxSources, Types.INTEGER)

    Util.printDebug("Search term(s): ")
    Util.printDebug(keywords)
    hrefs = []
    tries = 0

    while True:
        try:
            additionalSources = Math.floor(maxSources * 1.25)
            for result in DuckDuckGoSearch.DDGS().text(keywords, max_results=additionalSources):
                hrefs.append(result.get("href"))
            break
        except Exception as e:
            if tries >= 2:
                Util.printError("Couldn't load DuckDuckGo after 3 tries - aborting search.")
                break
            else:
                Util.printError("Exception thrown searching DuckDuckGo, trying again in 5 seconds...")
            if "202 Ratelimit" in str(e):
                Util.printError("(Rate limited - try opening DDG in a browser to reset the limit)")
            else:
                Util.printError("(" + str(e) + ")")
            Time.sleep(5)
            tries += 1
    return hrefs


def getSourceText(websiteIn, bypassLength, maxSentences):
    TypeCheck.enforce(websiteIn, Types.STRING)
    TypeCheck.enforce(bypassLength, Types.BOOLEAN)
    TypeCheck.enforce(maxSentences, Types.INTEGER)

    # TODO: stop the webpage after x seconds
    Util.printDebug("Getting text from: " + websiteIn)
    opt = Options.Options()
    # TODO: required for headless mode only, add accordingly
    opt.add_argument("--headless")
    opt.add_experimental_option("excludeSwitches", ["enable-automation"])
    opt.add_experimental_option("useAutomationExtension", False)
    opt.page_load_strategy = 'eager'
    driver = WebDriver.Chrome(options=opt)
    driver.set_page_load_timeout(30)
    driver.minimize_window()
    Stealth.stealth(
        driver,
        lanuages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    try:
        driver.get(websiteIn)
    except Exception as e:
        Util.printError("Could not fetch resource from website: " + websiteIn)
        Util.printError(str(e))
        return [websiteIn, None, None]

    UI.WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.By.XPATH, "/html/body")))
    websiteTitle = driver.title
    websiteText = driver.find_element(By.By.XPATH, "/html/body").text
    driver.quit()
    websiteText = Util.cleanupString(websiteText)
    matchJS = 0
    for s in __errorsJS:
        if s in websiteText:
            matchJS += 1
    if matchJS >= 3:
        Util.printError(f"Website failed JS test: {websiteIn}")
        return [websiteIn, websiteTitle, ""]
    for e in __errorsBlocked:
        if e in websiteText:
            Util.printError(f"Website failed error test: {websiteIn}")
            return [websiteIn, websiteTitle, ""]
    if not bypassLength and maxSentences > 0:
        trimmedText = Util.trimTextBySentenceLength(websiteText, maxSentences)
        Util.printDebug(f"Fetched trimmed text from: {websiteIn}")
        Util.printDump(trimmedText)
        return [websiteIn, websiteTitle, trimmedText]
    else:
        Util.printDebug(f"Retrieved text from: {websiteIn}")
        Util.printDump(websiteText)
        return [websiteIn, websiteTitle, websiteText]


def getYouTubeCaptions(videoIdIn):
    TypeCheck.enforce(videoIdIn, Types.STRING)

    try:
        captionStringBuilder = ""
        defaultLanguageCode = "en"
        Util.printDebug(f"Video ID: {videoIdIn}")
        srt = YouTubeTranscriptApi.YouTubeTranscriptApi().fetch(videoIdIn, languages=[defaultLanguageCode], preserve_formatting=True)
        if srt.is_generated:
            Util.printInfo("This transcript is auto-generated - it may not be correct.")
        for s in srt.snippets:
            if s.text is not None:
                captionStringBuilder += s.text + " "
        captionStringBuilder = captionStringBuilder.replace("\xa0", "")
        captionStringBuilder = Util.cleanupString(captionStringBuilder)
        Util.printDump(f"Video captions: {captionStringBuilder}")
        return captionStringBuilder
    except Exception as e:
        disabledText = "Subtitles are disabled for this video"
        if disabledText in str(e):
            Util.printError(f"{disabledText}.")
            return disabledText + "."
        else:
            Util.printError(str(e))
            return "An error occured obtaining the captions for this video."
