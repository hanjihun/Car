from sys import exit, argv
from os.path import abspath, isdir, join, isfile
from os import listdir, getcwd, remove, chdir, linesep
from os import name as os_name
from json import loads,dumps
from getopt import getopt, GetoptError

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging


USAGE = ('Usage: python spider_test_tool.py '+
         '[-u] <path_to_project_dir>'+
         linesep+
         '"-u" flag is for updating categories'
         )

try:
    opts, args = getopt(argv[1:], 'u')
except GetoptError as err:
    exit('Error: %s%s%s' % (str(err), linesep, USAGE))
else:
    # args check
    if not args:
        exit(USAGE)
    else:
        PROJECT_PATH = abspath(args[0])

    # validation of project path
    if not (isdir(PROJECT_PATH) and 'scrapy.cfg' in listdir(PROJECT_PATH)):
        exit('"%s" is not an appropriate path!' % PROJECT_PATH)
    else:
        MAIN_PATH = getcwd()
        chdir(PROJECT_PATH)

    update_categories = True if opts else False

###########################################################

VERSION = '0.1.4'

try:
    PROJECT_SETTINGS = get_project_settings()
    PROJECT_NAME = PROJECT_SETTINGS['BOT_NAME']
except KeyError:
    exit('There is no project name in scrapy.cfg!')

FEED_URI_PREFIX = 'file:///' if os_name!='posix' else '' 

FILE_PATHS = [join(MAIN_PATH, i % PROJECT_NAME) for i in (
              '%s_categories.json','%s_items.csv',
              '%s.log','%s_updating_categories.log')]

###########################################################

print ('Test utility (version: %s), project "%s"%s' %\
      (VERSION, PROJECT_NAME, linesep))

# check the past items and logs and removing them
map(remove, filter(isfile, FILE_PATHS))


if update_categories:
    print ('Updating the categories...')

    configure_logging({'LOG_FILE': FILE_PATHS[3]})
    PROJECT_SETTINGS.update({'ITEM_PIPELINES':{'CoreLib.CatsPipeline':1}})
    RUNNER = CrawlerRunner(PROJECT_SETTINGS)
    d = RUNNER.crawl('categories_of_%s' % PROJECT_NAME)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    exit('End of scraping.')


print ('Getting the categories...')

configure_logging({'LOG_FILE': FILE_PATHS[2]})
PROJECT_SETTINGS.update({'FEED_FORMAT':'json',
                         'FEED_URI': FEED_URI_PREFIX+FILE_PATHS[0]})
RUNNER = CrawlerRunner(PROJECT_SETTINGS)

def between_func():
    with open(FILE_PATHS[0]) as f:
        json = f.read()
        if not json: exit('There are no categories!')
        items = loads(json)

    remove(FILE_PATHS[0])

    cats_list = []
    for i in items:
        cats_list.extend(i['links'])

    print ('%s categories were extracted' % len(cats_list))

    global categories_json
    categories_json = dumps({c: str(i) for i,c in enumerate(cats_list)},
                            ensure_ascii=False)

    RUNNER.settings.update({'FEED_FORMAT':'csv',
                            'FEED_URI': FEED_URI_PREFIX+FILE_PATHS[1]})

    print (linesep + 'Scraping the site...')


@defer.inlineCallbacks
def crawl():
    yield RUNNER.crawl('categories_of_%s' % PROJECT_NAME)
    between_func()
    yield RUNNER.crawl('%s_spider' % PROJECT_NAME,
                       categories=categories_json)
    reactor.stop()

crawl()
reactor.run()

exit('End of scraping process')
