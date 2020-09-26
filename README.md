# meta search engine builder

This script builds the html pages for a little meta-search tool;

The html page [in action](https://mosermichael.github.io/duckduckbang/html/main.html) 

The page is kept up to date by a nightly build process (runs courtesy of [github workflows/actions](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions) )


# script that builds the page

The [build-cats.py](https://github.com/MoserMichael/duckduckbang/blob/master/build-cats.py) script that generates the search page works as follows: 

1. It loads the following url [https://duckduckgo.com/bang.js](https://duckduckgo.com/bang.js) this gives a json file that contains an entry for each bang! search operator, and the classification of the operator in the official [bang page](https://duckduckgo.com/bang) hierarchy.
2. builds the category/subcategory breakup that is used to display the [bang page](https://duckduckgo.com/bang).  
3. format an html page that contains all of the !bang operators into one page (maintain categories displayed in the official bang page)

The tool utilizes [duckduck go bang! operators](https://duckduckgo.com/bang)

# Reason for all this

Lately I have been increasingly using specialised search engines; for example when searching for code it is possible to find a lot in [github search](https://github.com/search/advanced) (the search operators are explained [here](https://docs.github.com/en/free-pro-team@latest/github/searching-for-information-on-github/searching-code) and  [here](https://docs.github.com/en/github/searching-for-information-on-github/understanding-the-search-syntax). 

Now general purpose search engines like google and bing have a hard time to give reasonable answers to each and every search request. Google has a hard job: it has identify the intent of your query and give you the stuff that is relevant to your query - they also have to be good for a very wide range of individuals.

Specialized search engines have it much easier - they don't have to work hard to determine the intent of the query, as they are focused on a particular domain.  Also they may have a more focused and sometimes deeper index on a particular domain; You might consider using a specialized search engine if you fail to find the stuff with google or bing. With duckduckgo you get this huge classification with the bang! search operator (that's where this project comes in). 

These specialized search engines will also tend to respect your privacy as they won't have the resources and data of the big players.

# today i learned

The abbreviation of Categories is cat; [here](https://writingexplained.org/english-abbreviations/category)
Are cats capable of categorization? No idea, I like them. 




