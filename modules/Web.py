# package modules


import concurrent as Concurrent
import duckduckgo_search as DuckDuckGoSearch
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


__errorsJS = []
__errorsBlocked = []


def __getWebConfiguration():
    global __errorsJS, __errorsBlocked
    webConfig = Operation.readFile(Path.CONFIGS_WEB_FILE_NAME, None, False)
    webConfig = Util.cleanupString(webConfig)
    if webConfig is not None:
        j = JSON.loads(webConfig)
        __errorsJS = j.get("js_errors")
        __errorsBlocked = j.get("web_errors")
    return


__getWebConfiguration()


####################
""" BEGIN SEARCH """
####################


def getSearchResultsTextAsync(hrefs, maxSentences):
    TypeCheck.check(hrefs, Types.LIST)
    TypeCheck.check(maxSentences, Types.INTEGER)

    searchResults = {}
    Util.printDebug("\nTarget links:")
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
                Util.printError("\nFailed to fetch a source.\n" + str(e))
                res = None
            if res is not None and not Util.checkEmptyString(res[2]):
                searchResults[res[0]] = res[2]
    if len(searchResults) == 0:
        Util.printError("\nNo sources were compiled!")
    return searchResults


def getSearchResults(keywords, maxSources):
    TypeCheck.check(keywords, Types.STRING)
    TypeCheck.check(maxSources, Types.INTEGER)

    Util.printDebug("\nSearch term(s):\n" + keywords)
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
                Util.printError("\nCouldn't load DuckDuckGo after 3 tries! Aborting search.")
                break
            else:
                Util.printError("\nException thrown searching DuckDuckGo, trying again in 5 seconds...")
            if "202 Ratelimit" in str(e):
                Util.printError("(Rate limited - try opening DDG in a browser to reset the limit)")
            else:
                Util.printError("(" + str(e) + ")")
            Time.sleep(5)
            tries += 1
    return hrefs


def getSourceText(websiteIn, bypassLength, maxSentences):
    TypeCheck.check(websiteIn, Types.STRING)
    TypeCheck.check(bypassLength, Types.BOOLEAN)
    TypeCheck.check(maxSentences, Types.INTEGER)

    # TODO: stop the webpage after x seconds
    Util.printDebug("\nGetting text from: " + websiteIn)
    opt = Options.Options()
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
        Util.printError("\nCould not fetch resource from website: " + websiteIn + "\n")
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
        Util.printError("\nWebsite failed JS test. (" + websiteIn + ")")
        return [websiteIn, websiteTitle, ""]
    for e in __errorsBlocked:
        if e in websiteText:
            Util.printError("\nWebsite failed error test. (" + websiteIn + ")")
            return [websiteIn, websiteTitle, ""]
    if not bypassLength and maxSentences > 0:
        trimmedText = Util.trimTextBySentenceLength(websiteText, maxSentences)
        Util.printDebug("\nFetched trimmed text from: " + websiteIn)
        Util.printDump(trimmedText)
        return [websiteIn, websiteTitle, trimmedText]
    else:
        Util.printDebug("\nFetched text from: " + websiteIn)
        Util.printDump(websiteText)
        return [websiteIn, websiteTitle, websiteText]


def getYouTubeCaptions(videoIdIn):
    TypeCheck.check(videoIdIn, Types.STRING)

    try:
        captionStringBuilder = ""
        defaultLanguageCode = "en"
        Util.printDebug("\nVideo ID: " + videoIdIn)
        srt = YouTubeTranscriptApi.YouTubeTranscriptApi.get_transcript(videoIdIn, languages=[defaultLanguageCode])
        if YouTubeTranscriptApi.YouTubeTranscriptApi.list_transcripts(videoIdIn).find_transcript([defaultLanguageCode]).is_generated:
            Util.printInfo("\nThis transcript is auto-generated - it may not be correct.")
        for s in srt:
            if s.get("text") is not None:
                captionStringBuilder += s["text"] + " "
        captionStringBuilder = captionStringBuilder.replace("\xa0", "")
        captionStringBuilder = Util.cleanupString(captionStringBuilder)
        Util.printDump("\nVideo captions: " + captionStringBuilder)
        return captionStringBuilder
    except Exception as e:
        disabledText = "Subtitles are disabled for this video"
        if disabledText in str(e):
            Util.printError("\n" + disabledText + "!")
            return disabledText + "."
        else:
            Util.printError("\n" + str(e))
            return "An error occured obtaining the captions for this video."
