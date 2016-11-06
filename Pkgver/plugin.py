###
# Copyright (c) 2016, Johannes Löthberg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from urllib.parse import quote
import json

import requests

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Pkgver')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Pkgver(callbacks.Plugin):
    """Look up Arch Linux package versions"""
    threaded = True

    def pkgver(self, irc, msg, args, query):
        """Look up Arch Linux package versions"""
        baseUrl = self.registryValue('archwebSearchUrl')
        url = '{}/json/?name={:s}'.format(baseUrl, quote(query))
        res = requests.get(url)

        results = {}
        for pkg in res.json()['results']:
            pkgname = pkg.get('pkgname')
            repo = pkg.get('repo')

            epoch = pkg.get('epoch')
            pkgver = pkg.get('pkgver')
            pkgrel = pkg.get('pkgrel')

            arch = pkg.get('arch')

            if epoch:
                version = '{}:{}-{}'.format(epoch, pkgver, pkgrel)
            else:
                version = '{}-{}'.format(pkgver, pkgrel)

            repo_pkgname = '{}/{}'.format(repo, pkgname)
            if repo_pkgname not in results:
                results[repo_pkgname] = {}

            if version not in results[repo_pkgname]:
                results[repo_pkgname][version] = []

            results[repo_pkgname][version].append(arch)

        output = []
        for pkg in results:
            line = '{}:'.format(pkg)

            for version in results[pkg]:
                arches = results[pkg][version]
                line += ' {}::{}'.format('/'.join(arches), version)

            output.append(line)

        irc.replies(output, joiner=' | ')

    pkgver = wrap(pkgver, ['something'])


Class = Pkgver


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
