# -*- coding: utf-8 -*-
# Author  :  Sxt
# Date    :  2018/6/9 14:07
import sys
import os
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "Jobbole"])
# execute(["scrapy", "crawl", "zhihu"])
# execute(["scrapy", "crawl", "zaker"])
execute(["scrapy", "crawl", "tieba"])