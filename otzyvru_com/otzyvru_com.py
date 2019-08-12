# -*- coding: utf-8 -*-

"""Main module."""
import datetime
import json
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SCRUBBER_IS_STARTED = 'Scrubber is started'
SCRUBBER_IS_FINISHED = 'Scrubber is finished'
STOP_BY_LIMIT = 'Scrubber is stop by limit'


class _Logger:
    def send_info(self, message):
        print('INFO: ' + message)

    def send_warning(self, message):
        print('WARNING: ' + message)

    def send_error(self, message):
        print('ERROR: ' + message)


class OtzyvruCom(object):
    BASE_URL = 'https://www.otzyvru.com'
    reviews = []
    show_count = 0
    count = 0
    logger = None

    def __init__(self, slug, logger=_Logger()):
        self.session = requests.Session()
        self.logger = logger
        self.slug = slug
        self.rating = Rating()

    def start(self, limit=None, start_page=1):
        self.logger.send_info(SCRUBBER_IS_STARTED)
        page = start_page
        one_page = self._get_page(page)
        self.rating.average_rating = one_page.find('span',
                                                   class_='average').text
        self.show_count = int(
            re.search(r'\d+', one_page.find('span', class_='rtngviews').text
                      ).group())

        self.count = int(one_page.select_one('div.rtngdescr>span.count').text)
        page += 1
        self.reviews.extend(self._collect_comments(one_page))
        while True:
            if limit and limit <= len(self.reviews):
                self.logger.send_info(STOP_BY_LIMIT)
                break
            self.logger.send_info('scrubbing page: %s...' % page)

            page_result = self._get_page(page)
            if len(page_result.select('div.commentbox')) == 0:
                break
            self.reviews.extend(self._collect_comments(self._get_page(page)))
            page += 1
        self.logger.send_info(SCRUBBER_IS_FINISHED)
        return self

    def _collect_comments(self, soup):
        for html_comment in soup.select('div.commentbox'):
            yield self._parse_comment(html_comment)

    def _get_page(self, page):
        time.sleep(1)
        response = self.session.get(
            urljoin(self.BASE_URL, self.slug) + '?page=%s' % page)
        if not response.status_code == 200:
            self.logger.send_error(response.text)
            raise Exception(response.text, response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def _parse_comment(self, soup_comment):
        new_comment = Review()
        new_comment.author = self._get_author_of_comment(soup_comment)
        try:
            new_comment.id = int(re.search(r'\d+',
                                           soup_comment.attrs['id']).group())
        except KeyError:
            new_comment.id = int(soup_comment.find('a', onclick='answer(this)').attrs['comment-id'])
        new_comment.text = self._get_text(soup_comment)
        new_comment.rating.average_rating = self \
            ._get_rating_of_comment(soup_comment)
        new_comment.date = self._get_date_of_comment(soup_comment)
        new_comment.title = self._get_title_of_comment(soup_comment)
        plus, minus = self._get_rating_plus_and_minus_of_comment(soup_comment)
        new_comment.plus = plus
        new_comment.minus = minus
        new_comment.advantages = self._get_advantages(soup_comment)
        new_comment.disadvantages = self._get_disadvantages(soup_comment)

        is_has_other_sub_comments = soup_comment\
            .find('a', onclick='Common.get_comments({},this)'
                                                    .format(new_comment.id))
        if is_has_other_sub_comments:
            sub_comments = self._get_sub_review(new_comment.id)
            if sub_comments:
                new_comment.sub_comments.extend(sub_comments)
        return new_comment

    def _get_sub_review(self, id_):
        self.logger.send_info('request to sub reviews: %s' % id_)
        response = self.session.post(urljoin(self.BASE_URL,
                                             '/ajax/get_comments/%s' % id_),
                          headers={
                              'X-Requested-With': 'XMLHttpRequest',
                              'Accept': 'application/json, '
                                        'text/javascript, */*; q=0.01'
                          })
        if response.status_code == 200:
            html_doc = json.loads(response.text)['html']
            soup = BeautifulSoup(html_doc, 'html.parser')
            return self._collect_comments(soup)

    @staticmethod
    def _get_text(soup_comment):
        return soup_comment.find('span', class_=['comment', 'description']).text

    @staticmethod
    def _get_author_of_comment(soup_comment):
        name = soup_comment.select_one('span.author_name>ins').text.strip()
        author = Author()
        author.name = name
        return author

    @staticmethod
    def _get_title_of_comment(soup_comment):
        h2 = soup_comment.select_one('h2')
        if h2:
            return h2.text
        return None

    @staticmethod
    def _get_date_of_comment(soup_comment):
        return soup_comment.find('span',
                                 title=re.compile('\d+-\d\d-\d\d'))\
                                                                .attrs['title']

    @staticmethod
    def _get_rating_of_comment(soup_comment):
        try:
            start_ring = soup_comment.find('span', class_='star_ring') \
                .select_one('span').attrs['style']
            start_ring = int(re.search(r'\d+', start_ring).group())
            return start_ring / 13
        except AttributeError:
            return None

    @staticmethod
    def _get_advantages(soup_comment):
        advantages = []
        advantages_soup = soup_comment.select('div.advantages>ol')
        for advantage_soup in advantages_soup:
            advantages.append(advantage_soup.text.strip())
        return advantages

    @staticmethod
    def _get_disadvantages(soup_comment):
        disadvantages = []
        disadvantages_soup = soup_comment.select('div.disadvantages>ol')
        for advantage_soup in disadvantages_soup:
            disadvantages.append(advantage_soup.text.strip())
        return disadvantages

    @staticmethod
    def _get_rating_plus_and_minus_of_comment(soup_comment):
        plus = minus = 0
        plus_soup = soup_comment.select_one(
            'div.comment_stats>span.comment_rate>ins.plus')
        minus_soup = soup_comment \
            .select_one('div.comment_stats>span.comment_rate>ins.minus')
        if plus_soup:
            plus = int(plus_soup.text)
        if minus_soup:
            minus = int(minus_soup.text)
        return plus, minus


class Rating:
    average_rating = ''
    on_scale = 5

    def get_dict(self):
        return {
            'average_rating': self.average_rating,
            'on_scale': self.on_scale,
        }


class Author:
    name = ''

    def get_dict(self):
        return {
            'name': self.name,
        }


class Review:
    min_scale = 5
    max_scale = 5

    def __init__(self):
        self.rating = Rating()
        self.id = 0
        self.title = ''
        self.text = ''
        self.date = ''
        self.author = Author()
        self.advantages = list()
        self.disadvantages = list()
        self.sub_comments = list()
        self.plus = 0
        self.minus = 0

    def get_text(self):
        return 'Текст: {}\n Плюсы: {}\n Минусы: {}'.format(
            self.text, '\n'.join(self.advantages), '\n'.join(self.disadvantages)
        )

    def get_dict(self):
        return {
            'id': self.id,
            'rating': self.rating.get_dict(),
            'title': self.title,
            'text': self.text,
            'date': self.date,
            'author': self.author.get_dict(),
            'advantages': self.advantages,
            'disadvantages': self.disadvantages,
            'plus': self.plus,
            'minus': self.minus,
            'sub_comments': [r.get_dict() for r in self.sub_comments],
        }

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.text[:50]

    def __repr__(self):
        if len(self.text) >= 50:
            return self.text
        return self.text[:50] + '...'


if __name__ == '__main__':
    prov = OtzyvruCom('mtt-mejregionalniy-tranzittelekom')
    prov.start()

    for r in prov.reviews:
        print(r.get_dict())
