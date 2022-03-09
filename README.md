# Meta search tool builder

This script builds the html pages for a little meta-search tool; The tool attempts to be a is a slightly better organized directory of the duckduckgo [bang!](https://duckduckgo.com/bang) search commands.

There are quite a few versions of the page, all generated dynamically, you can view the results here:


|                              | Desktop version | mobile version  |
|------------------------------|:---------------:|:---------------:|
|Using the Original text       | [link](https://mosermichael.github.io/duckduckbang/html/main.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile.html)                | 
|Auto translation to Chinese   | [link](https://mosermichael.github.io/duckduckbang/html/main_zh.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_zh.html)                |
|Auto translation to English   | [link](https://mosermichael.github.io/duckduckbang/html/main_en.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_en.html)                |
|Auto translation to French    | [link](https://mosermichael.github.io/duckduckbang/html/main_fr.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_fr.html)                |
|Auto translation to German    | [link](https://mosermichael.github.io/duckduckbang/html/main_de.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_gr.html)                |
|Auto translation to Russian   | [link](https://mosermichael.github.io/duckduckbang/html/main_ru.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_ru.html)                |
|Auto translation to Spanish   | [link](https://mosermichael.github.io/duckduckbang/html/main_es.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_es.html)                |
|Auto translation to Ukrainian | [link](https://mosermichael.github.io/duckduckbang/html/main_uk.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_uk.html)                |
|Auto translation to Japanese  | [link](https://mosermichael.github.io/duckduckbang/html/main_ja.html)                | [link](https://mosermichael.github.io/duckduckbang/html/main_mobile_ja.html)                |


You can select a duckduckgo  bang! search operator, the operator then appears in the seach input box, where you can add your query; A search query that includes the selected bang! operator is sent to https://duckduckgo - once you press enter press or the Go! button; duckducko then redirects the query to a search engine specified by the operator.

A web search on duckduckgo that includes a bang! search command is redirected to a specialized search engine (the most famous bang operator is g! - a web search is redirected to google search if the term g! is added to the query text); now duckduckgo maintains a directory of these bang! search commands, each of these commands stands for a different search engine that takes over the web search.

The meta-search tool has the advantage of having all duckduckgo bang! search commands in one page, it uses the same catalog of operators as duckduckgo. I think having all bang! operators on one page makes it easier to use the feature.

The page is kept up to date by a nightly build process (runs courtesy of [github workflows/actions](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions) ) Any new bang! operator should therefore appear in the search tool.

Update: This tool also made it to the Hacker News front page! [link](https://news.ycombinator.com/item?id=24618447); I really learned quite a bit from the comments section. Thanks for the feedback. Thanks!

# Motivation for the search tool 

Lately I have been increasingly using specialised search engines; for example when searching for code examples it is possible to find quite a lot with [github search](https://github.com/search/advanced) (the search operators are explained [here](https://docs.github.com/en/free-pro-team@latest/github/searching-for-information-on-github/searching-code) and [here](https://docs.github.com/en/github/searching-for-information-on-github/understanding-the-search-syntax). I have not been able to get the same quality results in any of the big search engines.

Now general purpose search engines like [google](https://google.com), [bing](https://bing.com) and [yandex](https://yandex.com/) have a hard time to give reasonable answers to each and every search request. Google has a hard job: it has identify the intent of your query and give you the stuff that is relevant to your query, and then sort the results by the internal score of 'ranking'. These results have to be good for a very wide range of individuals.

Specialized search engines have it much easier - they don't have to work hard to determine the intent of the query, as they are focused on a particular domain.  Also they may have a more focused and sometimes deeper index on a particular domain; You might consider using a specialized search engine if you fail to find the stuff with google or bing. With duckduckgo you get this huge classification with the bang! search operator (that's where this project comes in). 

These specialized search engines will also tend to respect your privacy, more than the big players do; specialized search engines might not have the resources to do much snooping anyway (this might not always be the case, depending on affiliation, etc. etc.)

# Script that builds the page

The [build_cats.py](https://github.com/MoserMichael/duckduckbang/blob/master/build_cats.py) script that generates the search page works as follows: 

1. It loads the following url [https://duckduckgo.com/bang.js](https://duckduckgo.com/bang.js) this gives a json file that contains an entry for each bang! search operator, and the classification of the operator in the official [bang page](https://duckduckgo.com/bang).
2. Builds the category/subcategory breakup that is used to display the [bang page](https://duckduckgo.com/bang).  
3. Formats an html page that contains all of the !bang operators into one page (maintain categories displayed in the official bang page)

The tool utilizes [duckduck go bang! operators](https://duckduckgo.com/bang)

# Today i learned

The abbreviation of Categories is cat; [here](https://writingexplained.org/english-abbreviations/category)
Are cats capable of categorization? No idea, I like them. 

And I still don't know if the correct spelling is metasearch, meta-search or meta search. Bother!

I was really in doubt what to do with the generation of the [search page](https://mosermichael.github.io/duckduckbang/html/main.html) ; 
In the end it is generated by a continuous integration job with [github actions](https://github.com/features/actions); which is free or open source projects like this one.
Now github actions are disabled after a while, when they don't see any action in the code of the repository; therefore the script changes a log file in the master branch as well, in order to avoid this. That's a bit of a cat and mouse game...

Also I am using expect to automate pushing stuff into the repo by the build script (see build subdirectory in this project); sometimes that's a useful tool to know.

