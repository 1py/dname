#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CONTRIBUTORS (sorted by surname)
# LUO, Pengkui <pengkui.luo@gmail.com>
#
# UPDATED ON
# 2013: 06/10, 06/12
#
print('Executing %s' %  __file__)

import unittest

import domainname


class Test_TKLD (unittest.TestCase):

    def test_tklds (self):
        d = 'a.mail.google.com'
        t2ld = domainname.get_t2ld (d)
        t3ld = domainname.get_t3ld (d, t2ld=t2ld)
        sld, tld = domainname.get_sld_tld (d, t2ld=t2ld)
        self.assertEqual(tld, 'com')
        self.assertEqual(t2ld, 'google.com')
        self.assertEqual(t3ld, 'mail.google.com')


if __name__ == '__main__':
    unittest.main()
