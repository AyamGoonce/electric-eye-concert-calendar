(function () {
  "use strict";

  var state = {
    artists: false,
    venues: false,
    genres: false,
    rendered: false
  };

  function normalize(value) {
    return (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function slugify(value) {
    return normalize(value).replace(/\s+/g, "-");
  }

  function sortKey(value) {
    var normalized = normalize(value);

    return normalized.replace(
      /^(?:the|a|an|le|la|les)\s+/,
      ""
    );
  }

  function firstLetter(value) {
    var key = sortKey(value);
    var character = key.charAt(0).toUpperCase();

    return /^[A-Z]$/.test(character) ? character : "#";
  }

  function sortItems(items) {
    return items.sort(function (a, b) {
      return sortKey(a.name).localeCompare(
        sortKey(b.name),
        "en",
        { sensitivity: "base" }
      );
    });
  }

  function filterItemsForQuery(items, query, artistSection) {
    var normalizedQuery = normalize(query);
    var exactArtistQuery = false;

    if (!normalizedQuery) {
      return items.filter(function (item) {
        return !item.searchOnly;
      });
    }

    if (artistSection) {
      exactArtistQuery = items.some(function (item) {
        return (item.exactTerms || []).some(function (term) {
          return normalize(term) === normalizedQuery;
        });
      });
    }

    return items.filter(function (item) {
      var searchable = [item.name, item.meta]
        .concat(item.searchTerms || [])
        .concat(item.exactTerms || [])
        .map(normalize);

      return searchable.some(function (value) {
        return exactArtistQuery
          ? value === normalizedQuery
          : value.indexOf(normalizedQuery) !== -1;
      });
    });
  }

  function hasEditorialCoverage(content, slug) {
    var artist =
      content &&
      content.artists &&
      content.artists[slug];

    return !!(
      artist &&
      artist.identity &&
      !artist.identity.hideFromArtistIndex &&
      Array.isArray(artist.da) &&
      artist.da.length
    );
  }

  function makeArtistItems() {
    var lookup =
      window.ElectricEyeArtistLookup &&
      window.ElectricEyeArtistLookup.terms;
    var content = window.ElectricEyeContentIndex;

    if (!lookup || !content || !content.artists) return null;

    var structuralRelationshipFields = [
      "members",
      "formerMembers",
      "associatedActs",
      "sideProjects"
    ];
    var searchTermsBySlug = Object.create(null);
    var scopedArticlesBySlug = Object.create(null);
    var entitiesBySlug = Object.create(null);
    var relationshipLookup = Object.create(null);
    var searchEdges = Object.create(null);

    function addSearchTerm(slug, value) {
      if (!slug || !value) return;

      if (!searchTermsBySlug[slug]) {
        searchTermsBySlug[slug] = [];
      }

      if (searchTermsBySlug[slug].indexOf(value) === -1) {
        searchTermsBySlug[slug].push(value);
      }
    }

    function addScopedArticle(slug, term, article) {
      var key = normalize(term);

      if (!slug || !key || !article || !article.u || !article.t) return;

      if (!scopedArticlesBySlug[slug]) {
        scopedArticlesBySlug[slug] = Object.create(null);
      }

      if (!scopedArticlesBySlug[slug][key]) {
        scopedArticlesBySlug[slug][key] = [];
      }

      if (
        !scopedArticlesBySlug[slug][key].some(function (item) {
          return item.href === article.u;
        })
      ) {
        scopedArticlesBySlug[slug][key].push({
          name: article.t,
          href: article.u,
          meta: article.d || ""
        });
      }
    }

    function addSearchEdge(fromSlug, toSlug) {
      if (!fromSlug || !toSlug || fromSlug === toSlug) return;

      if (!searchEdges[fromSlug]) {
        searchEdges[fromSlug] = [];
      }

      if (searchEdges[fromSlug].indexOf(toSlug) === -1) {
        searchEdges[fromSlug].push(toSlug);
      }
    }

    function registerEntity(slug, entity, isArtist) {
      var identity = entity.identity || {};
      var name = entity.n || identity.canonicalName || slug;
      var aliases = entity.al || [];

      entitiesBySlug[slug] = {
        name: name,
        aliases: aliases,
        identity: identity,
        isArtist: !!isArtist
      };

      [name].concat(aliases).forEach(function (value) {
        if (!value) return;
        relationshipLookup[value] = slug;
        relationshipLookup[normalize(value)] = slug;
      });
    }

    function resolveRelationshipSlug(name) {
      if (!name) return null;

      return (
        relationshipLookup[name] ||
        relationshipLookup[normalize(name)] ||
        lookup[name] ||
        lookup[normalize(name)] ||
        null
      );
    }

    Object.keys(content.artists).forEach(function (slug) {
      registerEntity(slug, content.artists[slug] || {}, true);
    });

    Object.keys(content.relationshipNodes || {}).forEach(function (slug) {
      registerEntity(
        slug,
        content.relationshipNodes[slug] || {},
        false
      );
    });

    Object.keys(entitiesBySlug).forEach(function (slug) {
      var entity = entitiesBySlug[slug];
      var identity = entity.identity || {};

      // Relationship metadata describes identity; only reviewed search fields
      // and reviewed structural fields may expand global search routing.
      // Collaborators are deliberately excluded: article co-subjects and
      // one-off billmates must not become global search equivalents.
      structuralRelationshipFields.forEach(function (field) {
        (identity[field] || []).forEach(function (relatedName) {
          var relatedSlug;
          var relatedEntity;

          if (
            entity.isArtist ||
            identity.searchResultVisible
          ) {
            addSearchTerm(slug, relatedName);
          }

          relatedSlug = resolveRelationshipSlug(relatedName);
          if (!relatedSlug) return;

          relatedEntity = entitiesBySlug[relatedSlug];

          if (
            relatedEntity &&
            (
              entity.isArtist ||
              identity.searchResultVisible
            )
          ) {
            [relatedEntity.name]
              .concat(relatedEntity.aliases || [])
              .forEach(function (relatedTerm) {
                addSearchTerm(slug, relatedTerm);
              });
          }

          addSearchEdge(slug, relatedSlug);

          if (!hasEditorialCoverage(content, slug)) return;

          addSearchEdge(relatedSlug, slug);

          if (
            relatedEntity &&
            (
              (
                relatedEntity.isArtist &&
                hasEditorialCoverage(content, relatedSlug)
              ) ||
              relatedEntity.identity.searchResultVisible
            )
          ) {
            [entity.name].concat(entity.aliases || []).forEach(
              function (term) {
                addSearchTerm(relatedSlug, term);
              }
            );
          }
        });
      });

      (identity.searchAssociations || []).forEach(function (relatedName) {
        if (entity.isArtist) {
          addSearchTerm(slug, relatedName);
        }

        var relatedSlug = resolveRelationshipSlug(relatedName);

        if (!relatedSlug) return;

        addSearchEdge(slug, relatedSlug);
        addSearchEdge(relatedSlug, slug);
      });

      (identity.searchLinks || []).forEach(function (relatedName) {
        if (entity.isArtist) {
          addSearchTerm(slug, relatedName);
        }

        var relatedSlug = resolveRelationshipSlug(relatedName);

        if (
          relatedSlug &&
          !hasEditorialCoverage(content, slug)
        ) {
          addSearchEdge(slug, relatedSlug);
        }
      });

    });

    Object.keys(entitiesBySlug).forEach(function (sourceSlug) {
      if (hasEditorialCoverage(content, sourceSlug)) {
        return;
      }

      var source = entitiesBySlug[sourceSlug];
      var sourceTerms = [source.name].concat(source.aliases || []);
      var queue = [sourceSlug];
      var visited = Object.create(null);

      visited[sourceSlug] = true;

      while (queue.length) {
        var currentSlug = queue.shift();

        (searchEdges[currentSlug] || []).forEach(function (targetSlug) {
          if (visited[targetSlug]) return;

          visited[targetSlug] = true;

          var targetIsVisible = hasEditorialCoverage(
            content,
            targetSlug
          );

          if (targetIsVisible) {
            sourceTerms.filter(function (term) {
              var aliasLinks = source.identity.searchAliasLinks || {};
              var reviewedTargets = null;

              Object.keys(aliasLinks).some(function (alias) {
                if (normalize(alias) !== normalize(term)) return false;
                reviewedTargets = aliasLinks[alias] || [];
                return true;
              });

              if (!reviewedTargets) return true;

              return reviewedTargets.some(function (targetName) {
                return resolveRelationshipSlug(targetName) === targetSlug;
              });
            }).forEach(function (term) {
              addSearchTerm(targetSlug, term);
            });

            (source.identity.searchArticleIds || []).forEach(
              function (postId) {
                (content.articles || []).forEach(function (article) {
                  if (String(article.pi || "") !== String(postId)) return;

                  sourceTerms.forEach(function (term) {
                    addScopedArticle(targetSlug, term, article);
                  });
                });
              }
            );
          } else {
            queue.push(targetSlug);
          }
        });
      }
    });

    Object.keys(content.artists).forEach(function (slug) {
      var artist = content.artists[slug] || {};

      (artist.al || []).forEach(function (alias) {
        addSearchTerm(slug, alias);
      });
    });

    return sortItems(
      Object.keys(content.artists)
        .filter(function (slug) {
          var artist = content.artists[slug] || {};
          var identity = artist.identity || {};

          return (
            hasEditorialCoverage(content, slug) ||
            identity.searchResultVisible === true
          );
        })
        .map(function (slug) {
          var artist = content.artists[slug] || {};
          var identity = artist.identity || {};
          var name = artist.n || slug;
          var exactTerms = [name]
            .concat(artist.al || []);

          var articleItems = [];
          var seenArticleUrls = Object.create(null);
          (artist.ar || []).forEach(
              function (articleIndex) {
                var article =
                  content.articles &&
                  content.articles[articleIndex];

                if (
                  !article ||
                  !article.t ||
                  !article.u ||
                  seenArticleUrls[article.u]
                ) {
                  return;
                }

                seenArticleUrls[article.u] = true;

                articleItems.push({
                  articleIndex: articleIndex,
                  name: article.t,
                  href: article.u,
                  meta: article.d || ""
                });
              }
            );

          return {
            slug: slug,
            name: name,
            href:
              "https://archive.electriceyerock.com/artist/" +
              slug +
              "/",
            meta: "",
            searchTerms: searchTermsBySlug[slug] || [],
            exactTerms: exactTerms,
            aliasTerms: artist.al || [],
            articleItems: articleItems,
            scopedArticleItems: scopedArticlesBySlug[slug] || {}
          };
        })
        .concat(
          Object.keys(content.relationshipNodes || {})
            .filter(function (slug) {
              var node = content.relationshipNodes[slug] || {};
              return !!(
                node.identity &&
                node.identity.searchResultVisible
              );
            })
            .map(function (slug) {
              var node = content.relationshipNodes[slug] || {};
              var name = node.n || slug;

              return {
                slug: slug,
                name: name,
                href: "",
                meta: "",
                searchOnly: true,
                searchTerms: searchTermsBySlug[slug] || [],
                exactTerms: [name].concat(node.al || []),
                aliasTerms: node.al || [],
                articleItems: [],
                scopedArticleItems: {}
              };
            })
        )
    );
  }

  function makeVenueItems() {
    var data = window.ElectricEyeVenueData;

    if (!data) return null;

    return sortItems(
      Object.keys(data)
        .filter(function (key) {
          var venue = data[key] || {};

          return (
            (Array.isArray(venue.articles) &&
              venue.articles.length > 0) ||
            (Array.isArray(venue.events) &&
              venue.events.length > 0)
          );
        })
        .map(function (key) {
          var venue = data[key] || {};
          var name = venue.name || key;
          var city = venue.city || "";
          var events = venue.events || [];

          if (!city && events.length) {
            city = events[0].city || "";
          }

          return {
            name: name,
            href:
              "https://www.electriceyerock.com/p/venues.html#venue-" +
              slugify(name),
            meta: city,
            address: venue.address || "",
            website: venue.website || "",
            exactTerms: [name],
            aliasTerms: []
              .concat(venue.aliases || [])
              .concat(venue.formerNames || [])
              .concat(venue.currentName || []),
            searchTerms: []
              .concat(venue.aliases || [])
              .concat(venue.formerNames || [])
              .concat(venue.currentName || [])
          };
        })
    );
  }

  function makeGenreItems() {
    var data = window.ElectricEyeGenreData;
    var lookup =
      window.ElectricEyeArtistLookup &&
      window.ElectricEyeArtistLookup.terms;
    var content = window.ElectricEyeContentIndex;
    var concerts = window.ElectricEyeConcertData;

    if (
      !data ||
      !Array.isArray(data.genres) ||
      !lookup ||
      !content ||
      !content.artists ||
      !Array.isArray(concerts)
    ) {
      return null;
    }

    var calendarArtists = Object.create(null);

    concerts.forEach(function (event) {
      [event.h]
        .concat(event.ch || [], event.o || [])
        .filter(Boolean)
        .forEach(function (name) {
          calendarArtists[normalize(name)] = true;
        });
    });

    var items = data.genres.map(function (genre) {
      var visibleArtists = (genre.artists || []).filter(
        function (name) {
          var slug = lookup[name];
          var articleBacked =
            slug && hasEditorialCoverage(content, slug);
          var calendarBacked =
            !!calendarArtists[normalize(name)];

          return articleBacked || calendarBacked;
        }
      );

      return {
        name: genre.name,
        parent: genre.parent || "",
        href:
          "https://archive.electriceyerock.com/genre/" +
          slugify(genre.name) +
          "/",
        artistCount: visibleArtists.length,
        articleBackedArtistCount: visibleArtists.filter(function (name) {
          var slug = lookup[name];
          return slug && hasEditorialCoverage(content, slug);
        }).length
      };
    });

    var byName = Object.create(null);
    var children = Object.create(null);

    items.forEach(function (item) {
      byName[item.name] = item;
      children[item.name] = [];
    });

    items.forEach(function (item) {
      if (item.parent && byName[item.parent]) {
        children[item.parent].push(item);
      }
    });

    var keepMemo = Object.create(null);

    function shouldKeep(item) {
      if (Object.prototype.hasOwnProperty.call(keepMemo, item.name)) {
        return keepMemo[item.name];
      }

      var keep =
        item.artistCount >= 1 ||
        children[item.name].some(shouldKeep);

      keepMemo[item.name] = keep;
      return keep;
    }

    return sortItems(items.filter(shouldKeep));
  }

  var GLOBAL_RESULT_LIMIT = 8;
  var GLOBAL_GROUPS = [
    { key: "artists", label: "Artists" },
    { key: "concerts", label: "Concerts" },
    { key: "articles", label: "Articles" },
    { key: "venues", label: "Venues" },
    { key: "genres", label: "Genres" }
  ];
  var ARTICLE_TYPE_LABELS = {
    concert_review: "Concert Review",
    interview: "Interview",
    album_review: "Album Review",
    news: "News",
    playlist: "Playlist",
    other: "Article"
  };

  function uniqueNormalized(values) {
    var seen = Object.create(null);

    return (values || []).map(normalize).filter(function (value) {
      if (!value || seen[value]) return false;
      seen[value] = true;
      return true;
    });
  }

  function prepareSearchTerms(canonical, aliases, other) {
    var canonicalTerms = uniqueNormalized(canonical);
    var aliasTerms = uniqueNormalized(aliases);
    var otherTerms = uniqueNormalized(other);

    return {
      canonical: canonicalTerms,
      aliases: aliasTerms,
      other: otherTerms,
      all: uniqueNormalized(
        canonicalTerms.concat(aliasTerms, otherTerms)
      )
    };
  }

  function startsWithQuery(value, query) {
    return value.indexOf(query) === 0;
  }

  function containsQueryTokens(value, query) {
    var valueTokens = value.split(" ");
    var queryTokens = query.split(" ");

    return queryTokens.every(function (token) {
      return token && valueTokens.indexOf(token) !== -1;
    });
  }

  function anyTerm(terms, predicate) {
    return (terms || []).some(predicate);
  }

  function scoreSearchTerms(search, query, allowSubstring) {
    if (!query) return Infinity;

    if (anyTerm(search.canonical, function (term) {
      return term === query;
    })) return 0;

    if (anyTerm(search.aliases, function (term) {
      return term === query;
    })) return 10;

    if (anyTerm(search.canonical, function (term) {
      return startsWithQuery(term, query);
    })) return 20;

    if (anyTerm(search.aliases, function (term) {
      return startsWithQuery(term, query);
    })) return 30;

    if (
      anyTerm(
        search.all,
        function (term) {
          return containsQueryTokens(term, query);
        }
      )
    ) return 40;

    if (
      allowSubstring &&
      query.length >= 3 &&
      anyTerm(
        search.all,
        function (term) {
          return term.indexOf(query) !== -1;
        }
      )
    ) return 50;

    return Infinity;
  }

  function formatSearchDate(value) {
    if (!value) return "";

    try {
      return new Intl.DateTimeFormat("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
        timeZone: "UTC"
      }).format(new Date(value.slice(0, 10) + "T12:00:00Z"));
    } catch (_error) {
      return value;
    }
  }

  function buildArticleSearchItems(artistItems) {
    var content = window.ElectricEyeContentIndex;
    var articleTerms = [];
    var itemsBySlug = Object.create(null);
    var articleIndexByUrl = Object.create(null);

    if (!content || !Array.isArray(content.articles)) return [];

    content.articles.forEach(function (article, articleIndex) {
      articleTerms[articleIndex] = {
        canonical: [],
        aliases: [],
        scoped: []
      };

      if (article && article.u) {
        articleIndexByUrl[article.u] = articleIndex;
      }
    });

    artistItems.forEach(function (item) {
      if (!item.slug || !item.href) return;

      itemsBySlug[item.slug] = item;

      var artist = content.artists[item.slug] || {};

      (artist.ar || []).forEach(function (articleIndex) {
        var terms = articleTerms[articleIndex];
        if (!terms) return;

        terms.canonical.push(item.name);
        terms.aliases = terms.aliases.concat(item.aliasTerms || []);
      });

      Object.keys(item.scopedArticleItems || {}).forEach(function (term) {
        (item.scopedArticleItems[term] || []).forEach(function (article) {
          var articleIndex = articleIndexByUrl[article.href];
          var terms = articleTerms[articleIndex];

          if (terms) terms.scoped.push(term);
        });
      });
    });

    // Retain forward associations as a fallback for historical records while
    // applying the same artist visibility gate as the Artist result group.
    content.articles.forEach(function (article, articleIndex) {
      (article.a || []).forEach(function (slug) {
        var item = itemsBySlug[slug];
        var terms = articleTerms[articleIndex];

        if (!item || !item.href || !terms) return;
        terms.canonical.push(item.name);
        terms.aliases = terms.aliases.concat(item.aliasTerms || []);
      });
    });

    return content.articles.map(function (article, articleIndex) {
      var terms = articleTerms[articleIndex];
      var kind = ARTICLE_TYPE_LABELS[article.y] || "Article";
      var date = article.d || "";

      return {
        name: article.t || "Untitled article",
        href: article.u || "",
        meta: [formatSearchDate(date), kind].filter(Boolean).join(" · "),
        date: date,
        search: prepareSearchTerms(
          [article.t],
          terms.canonical.concat(terms.aliases),
          [article.y, kind, date, date.slice(0, 4)].concat(
            terms.scoped
          )
        ),
        taxonomySearch: prepareSearchTerms(article.l || [], [], [])
      };
    }).filter(function (item) {
      return !!item.href;
    });
  }

  function prepareArtistSearchItems(artistItems) {
    return artistItems.map(function (item) {
      item.globalSearch = prepareSearchTerms(
        [item.name],
        item.aliasTerms || [],
        item.searchTerms || []
      );
      item.exactLookup = Object.create(null);

      uniqueNormalized(item.exactTerms || [item.name]).forEach(
        function (term) {
          item.exactLookup[term] = true;
        }
      );

      return item;
    });
  }

  function resolveArtistTargets(artistItems, query) {
    return artistItems.map(function (item) {
      return {
        item: item,
        score: scoreSearchTerms(item.globalSearch, query, true)
      };
    }).filter(function (match) {
      // Only navigable, legitimate artist results may qualify a structured
      // bill. Hidden relationship nodes have already routed their terms onto
      // those targets inside makeArtistItems().
      return match.item.href && Number.isFinite(match.score);
    });
  }

  function eventBill(event) {
    return [
      { name: event.h, role: 0 }
    ].concat(
      (event.ch || []).map(function (name) {
        return { name: name, role: 1 };
      }),
      (event.o || []).map(function (name) {
        return { name: name, role: 2 };
      })
    ).filter(function (item) {
      return !!item.name;
    });
  }

  function prepareConcertSearchItems(events) {
    return (events || []).map(function (event) {
      return {
        name: concertName(event),
        href: concertHref(event),
        meta: concertMeta(event),
        date: event.d || "",
        bill: eventBill(event).map(function (bill) {
          return {
            identity: normalize(bill.name),
            role: bill.role,
            search: prepareSearchTerms([bill.name], [], [])
          };
        }),
        metadataSearch: prepareSearchTerms([], [], [
          event.v,
          event.c,
          event.et,
          event.fn,
          event.d,
          (event.d || "").slice(0, 4),
          event.st
        ]),
        taxonomySearch: prepareSearchTerms(event.x || [], [], [])
      };
    });
  }

  function resolvedConcertScore(concert, targets) {
    var best = Infinity;

    concert.bill.forEach(function (bill) {
      targets.forEach(function (target) {
        if (!target.item.exactLookup[bill.identity]) return;
        best = Math.min(best, target.score + bill.role);
      });
    });

    return best;
  }

  function directConcertScore(concert, query) {
    var best = Infinity;

    concert.bill.forEach(function (bill) {
      best = Math.min(
        best,
        scoreSearchTerms(bill.search, query, true) + bill.role
      );
    });

    var metadataScore = scoreSearchTerms(
      concert.metadataSearch,
      query,
      true
    );

    var taxonomyScore = scoreSearchTerms(
      concert.taxonomySearch,
      query,
      false
    );

    return Math.min(best, metadataScore, taxonomyScore);
  }

  function concertHref(event) {
    if (Array.isArray(event.ee) && event.ee.length) {
      return "https://archive.electriceyerock.com/concert/" +
        event.i + "/";
    }

    return "https://www.electriceyerock.com/p/" +
      "paris-area-concert-calendar.html#event-" + event.i;
  }

  function concertName(event) {
    var names = [event.h].concat(event.ch || []).filter(Boolean);
    return names.join(" + ");
  }

  function concertMeta(event) {
    var venue = event.v || "";
    var city = event.c || "";

    if (city && normalize(city) !== "paris") {
      venue += " (" + city + ")";
    }

    return [formatSearchDate(event.d), venue]
      .filter(Boolean)
      .join(" · ");
  }

  function buildGlobalSearchData(artistItems, venueItems, genreItems) {
    var artists = prepareArtistSearchItems(artistItems);

    return {
      artists: artists,
      articles: buildArticleSearchItems(artists),
      concerts: prepareConcertSearchItems(
        window.ElectricEyeConcertData || []
      ),
      venues: venueItems.map(function (item) {
        item.globalSearch = prepareSearchTerms(
          [item.name],
          item.aliasTerms || [],
          [item.meta, item.address]
        );
        return item;
      }),
      genres: genreItems.map(function (item) {
        item.globalSearch = prepareSearchTerms([item.name], [], []);
        return item;
      })
    };
  }

  function compareNamedResults(a, b) {
    return a.score - b.score ||
      sortKey(a.name).localeCompare(sortKey(b.name), "en", {
        sensitivity: "base"
      }) ||
      a.href.localeCompare(b.href);
  }

  function searchGlobalData(data, rawQuery) {
    var query = normalize(rawQuery);
    var results = {
      artists: [],
      concerts: [],
      articles: [],
      venues: [],
      genres: []
    };

    if (!query) return results;

    results.artists = data.artists.map(function (item) {
      return {
        name: item.name,
        href: item.href,
        meta: item.searchOnly ? "Search relationship" : "Artist",
        score: scoreSearchTerms(item.globalSearch, query, true)
      };
    }).filter(function (item) {
      return Number.isFinite(item.score);
    }).sort(compareNamedResults);

    var artistTargets = resolveArtistTargets(data.artists, query);

    results.concerts = data.concerts.map(function (concert) {
      return {
        name: concert.name,
        href: concert.href,
        meta: concert.meta,
        date: concert.date,
        score: Math.min(
          directConcertScore(concert, query),
          resolvedConcertScore(concert, artistTargets)
        )
      };
    }).filter(function (item) {
      return Number.isFinite(item.score);
    }).sort(function (a, b) {
      return a.score - b.score ||
        a.date.localeCompare(b.date) ||
        compareNamedResults(a, b);
    });

    results.articles = data.articles.map(function (item) {
      return {
        name: item.name,
        href: item.href,
        meta: item.meta,
        date: item.date,
        score: Math.min(
          scoreSearchTerms(item.search, query, true),
          scoreSearchTerms(item.taxonomySearch, query, false)
        )
      };
    }).filter(function (item) {
      return Number.isFinite(item.score);
    }).sort(function (a, b) {
      return a.score - b.score ||
        b.date.localeCompare(a.date) ||
        compareNamedResults(a, b);
    });

    results.venues = data.venues.map(function (item) {
      return {
        name: item.name,
        href: item.href,
        meta: item.meta,
        score: scoreSearchTerms(item.globalSearch, query, true)
      };
    }).filter(function (item) {
      return Number.isFinite(item.score);
    }).sort(compareNamedResults);

    results.genres = data.genres.map(function (item) {
      return {
        name: item.name,
        href: item.href,
        meta: item.parent ? "Subgenre of " + item.parent : "Genre",
        score: scoreSearchTerms(item.globalSearch, query, false)
      };
    }).filter(function (item) {
      return Number.isFinite(item.score);
    }).sort(compareNamedResults);

    return results;
  }

  function setupGlobalSearch(data) {
    var form = document.getElementById("ee-global-search-form");
    var input = document.getElementById("ee-global-search-input");
    var clear = document.getElementById("ee-global-search-clear");
    var status = document.getElementById("ee-global-search-status");
    var container = document.getElementById("ee-global-search-results");
    var expandedGroups = Object.create(null);

    if (!form || !input || !clear || !status || !container) return;

    function updateQueryUrl(value) {
      var url = new URL(window.location.href);
      var trimmed = value.trim();

      if (trimmed) {
        url.searchParams.set("q", trimmed);
      } else {
        url.searchParams.delete("q");
      }

      window.history.replaceState({}, "", url.pathname + url.search + url.hash);
    }

    function focusableResults() {
      return Array.prototype.slice.call(
        container.querySelectorAll("a, button")
      ).filter(function (element) {
        return !element.hidden;
      });
    }

    function clearSearch() {
      input.value = "";
      expandedGroups = Object.create(null);
      updateQueryUrl("");
      render();
      input.focus();
    }

    function createGlobalResult(item) {
      var listItem = document.createElement("li");
      var label = document.createElement(item.href ? "a" : "span");

      listItem.className = "ee-global-result";
      label.className = "ee-global-result-link";
      label.textContent = item.name;
      if (item.href) label.href = item.href;
      listItem.appendChild(label);

      if (item.meta) {
        var meta = document.createElement("span");
        meta.className = "ee-global-result-meta";
        meta.textContent = item.meta;
        listItem.appendChild(meta);
      }

      return listItem;
    }

    function render() {
      var query = input.value;
      var normalizedQuery = normalize(query);
      var results = searchGlobalData(data, query);
      var total = 0;
      var groupCount = 0;

      container.innerHTML = "";
      clear.hidden = !normalizedQuery;

      if (!normalizedQuery) {
        container.hidden = true;
        status.textContent = "";
        input.setAttribute("aria-expanded", "false");
        return;
      }

      GLOBAL_GROUPS.forEach(function (groupDefinition) {
        var groupResults = results[groupDefinition.key] || [];

        if (!groupResults.length) return;

        total += groupResults.length;
        groupCount += 1;

        var section = document.createElement("section");
        var heading = document.createElement("h2");
        var count = document.createElement("span");
        var list = document.createElement("ul");
        var expanded = !!expandedGroups[groupDefinition.key];
        var visible = expanded
          ? groupResults
          : groupResults.slice(0, GLOBAL_RESULT_LIMIT);

        section.className = "ee-global-group";
        heading.className = "ee-global-group-heading";
        heading.textContent = groupDefinition.label;
        count.className = "ee-global-group-count";
        count.textContent = groupResults.length.toLocaleString("en");
        heading.appendChild(count);
        list.className = "ee-global-result-list";

        visible.forEach(function (item) {
          list.appendChild(createGlobalResult(item));
        });

        section.appendChild(heading);
        section.appendChild(list);

        if (groupResults.length > GLOBAL_RESULT_LIMIT) {
          var showAll = document.createElement("button");

          showAll.type = "button";
          showAll.className = "ee-global-show-all";
          showAll.textContent = expanded
            ? "Show fewer"
            : "Show all " + groupResults.length;
          showAll.setAttribute("aria-expanded", expanded ? "true" : "false");
          showAll.addEventListener("click", function () {
            expandedGroups[groupDefinition.key] = !expanded;
            render();
          });
          section.appendChild(showAll);
        }

        container.appendChild(section);
      });

      container.hidden = false;
      input.setAttribute("aria-expanded", groupCount ? "true" : "false");
      status.textContent = total
        ? total.toLocaleString("en") +
          (total === 1 ? " result" : " results") +
          " in " + groupCount.toLocaleString("en") +
          (groupCount === 1 ? " group." : " groups.")
        : "No matches found.";

      if (!groupCount) {
        var empty = document.createElement("p");
        empty.className = "ee-global-empty";
        empty.textContent = "No matches found.";
        container.appendChild(empty);
      }
    }

    function moveResultFocus(event, direction) {
      var focusable = focusableResults();
      var current = focusable.indexOf(document.activeElement);
      var next;

      if (!focusable.length) return;

      event.preventDefault();

      if (current === -1) {
        next = direction > 0 ? 0 : focusable.length - 1;
      } else {
        next = (current + direction + focusable.length) % focusable.length;
      }

      focusable[next].focus();
    }

    input.addEventListener("input", function () {
      expandedGroups = Object.create(null);
      updateQueryUrl(input.value);
      render();
    });

    input.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") moveResultFocus(event, 1);
      if (event.key === "ArrowUp") moveResultFocus(event, -1);
      if (event.key === "Escape" && input.value) {
        event.preventDefault();
        clearSearch();
      }
    });

    container.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") moveResultFocus(event, 1);
      if (event.key === "ArrowUp") moveResultFocus(event, -1);
      if (event.key === "Escape") {
        event.preventDefault();
        clearSearch();
      }
    });

    clear.addEventListener("click", clearSearch);

    form.addEventListener("submit", function (event) {
      var firstLink = container.querySelector("a");
      event.preventDefault();
      if (firstLink) firstLink.click();
    });

    window.addEventListener("popstate", function () {
      input.value = new URL(window.location.href).searchParams.get("q") || "";
      expandedGroups = Object.create(null);
      render();
    });

    input.value = new URL(window.location.href).searchParams.get("q") || "";
    render();
  }

  function setupCollapsible(section) {
    var heading = section.querySelector(".ee-index-heading");
    var body = section.querySelector(".ee-index-body");

    if (!heading || !body) return;

    function setOpen(open) {
      heading.setAttribute("aria-expanded", open ? "true" : "false");
      body.hidden = !open;
      section.classList.toggle("is-open", open);
    }

    heading.addEventListener("click", function () {
      setOpen(heading.getAttribute("aria-expanded") !== "true");
    });

    setOpen(false);
  }

  function createAlphabet(items, section) {
    var alphabet = section.querySelector(".ee-index-alphabet");
    var available = Object.create(null);

    if (!alphabet) return;

    items.forEach(function (item) {
      if (item.searchOnly) return;
      available[firstLetter(item.name)] = true;
    });

    ["#"].concat("ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")).forEach(
      function (letter) {
        var button = document.createElement("button");

        button.type = "button";
        button.className = "ee-index-letter";
        button.textContent = letter;
        button.dataset.letter = letter;

        if (!available[letter]) {
          button.disabled = true;
        }

        alphabet.appendChild(button);
      }
    );
  }

  function createItem(item) {
    var wrapper = document.createElement("div");
    var label = document.createElement(item.href ? "a" : "span");

    wrapper.className = "ee-index-item";

    if (item.href) label.href = item.href;
    label.textContent = item.name;
    wrapper.appendChild(label);

    if (item.meta) {
      var meta = document.createElement("span");

      meta.className = "ee-index-meta";
      meta.textContent = item.meta;
      wrapper.appendChild(meta);
    }

    return wrapper;
  }

  function renderItems(section, items, query, activeLetter) {
    var results = section.querySelector(".ee-index-results");
    var normalizedQuery = normalize(query);
    var groups = Object.create(null);

    results.innerHTML = "";

    var filtered = filterItemsForQuery(
      items,
      query,
      section.id === "ee-index-artists"
    ).filter(function (item) {
      if (
        activeLetter &&
        firstLetter(item.name) !== activeLetter
      ) {
        return false;
      }

      return true;
    });

    if (!filtered.length) {
      var empty = document.createElement("p");

      empty.className = "ee-index-empty";
      empty.textContent = "No matches found.";
      results.appendChild(empty);
      return;
    }

    filtered.forEach(function (item) {
      var letter = firstLetter(item.name);

      if (!groups[letter]) groups[letter] = [];
      groups[letter].push(item);
    });

    ["#"].concat("ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")).forEach(
      function (letter) {
        if (!groups[letter]) return;

        var group = document.createElement("section");
        var heading = document.createElement("h3");
        var itemGrid = document.createElement("div");

        group.className = "ee-index-group";
        group.dataset.letter = letter;

        heading.className = "ee-index-group-letter";
        heading.textContent = letter;

        itemGrid.className = "ee-index-items";

        groups[letter].forEach(function (item) {
          itemGrid.appendChild(createItem(item));
        });

        group.appendChild(heading);
        group.appendChild(itemGrid);
        results.appendChild(group);
      }
    );

    if (
      section.id === "ee-index-artists" &&
      normalizedQuery
    ) {
      var matchedArticles = [];
      var seenArticleUrls = Object.create(null);

      items.forEach(function (item) {
        var exactMatch = (item.exactTerms || []).some(
          function (term) {
            return normalize(term) === normalizedQuery;
          }
        );

        if (exactMatch) {
          (item.articleItems || []).forEach(function (article) {
            if (seenArticleUrls[article.href]) return;

            seenArticleUrls[article.href] = true;
            matchedArticles.push(article);
          });
        }

        (
          (item.scopedArticleItems || {})[normalizedQuery] || []
        ).forEach(function (article) {
          if (seenArticleUrls[article.href]) return;

          seenArticleUrls[article.href] = true;
          matchedArticles.push(article);
        });
      });

      if (matchedArticles.length) {
        var articleGroup = document.createElement("section");
        var articleHeading = document.createElement("h3");
        var articleGrid = document.createElement("div");

        articleGroup.className =
          "ee-index-group ee-index-article-results";

        articleHeading.className = "ee-index-group-letter";
        articleHeading.textContent = "Articles";

        articleGrid.className = "ee-index-items";

        matchedArticles.forEach(function (article) {
          articleGrid.appendChild(createItem(article));
        });

        articleGroup.appendChild(articleHeading);
        articleGroup.appendChild(articleGrid);
        results.appendChild(articleGroup);
      }
    }
  }

  function setupSection(id, items) {
    var section = document.getElementById(id);

    if (!section) return;

    var input = section.querySelector(".ee-index-search");
    var count = section.querySelector(".ee-index-count");
    var activeLetter = "";
    var visibleItemCount = items.filter(function (item) {
      return !item.searchOnly;
    }).length;

    count.textContent =
      visibleItemCount.toLocaleString("en") +
      (visibleItemCount === 1 ? " entry" : " entries");

    createAlphabet(items, section);
    renderItems(section, items, "", "");
    setupCollapsible(section);

    input.addEventListener("input", function () {
      activeLetter = "";

      section
        .querySelectorAll(".ee-index-letter")
        .forEach(function (button) {
          button.classList.remove("is-active");
        });

      renderItems(section, items, input.value, "");
    });

    section
      .querySelector(".ee-index-alphabet")
      .addEventListener("click", function (event) {
        var button = event.target.closest(".ee-index-letter");

        if (!button || button.disabled) return;

        if (activeLetter === button.dataset.letter) {
          activeLetter = "";
          button.classList.remove("is-active");
        } else {
          activeLetter = button.dataset.letter;

          section
            .querySelectorAll(".ee-index-letter")
            .forEach(function (candidate) {
              candidate.classList.toggle(
                "is-active",
                candidate === button
              );
            });
        }

        renderItems(
          section,
          items,
          input.value,
          activeLetter
        );
      });
  }

  function buildGenreTree(items) {
    var byName = Object.create(null);
    var children = Object.create(null);
    var roots = [];

    items.forEach(function (item) {
      byName[item.name] = item;
      children[item.name] = [];
    });

    items.forEach(function (item) {
      if (item.parent && byName[item.parent]) {
        children[item.parent].push(item);
      } else {
        roots.push(item);
      }
    });

    Object.keys(children).forEach(function (name) {
      sortItems(children[name]);
    });

    sortItems(roots);

    return {
      roots: roots,
      children: children
    };
  }

  function genreMatches(item, tree, query) {
    if (!query) return true;

    if (normalize(item.name).indexOf(query) !== -1) {
      return true;
    }

    return tree.children[item.name].some(function (child) {
      return genreMatches(child, tree, query);
    });
  }

  function createGenreNode(item, tree, query, ancestorMatched) {
    var children = tree.children[item.name] || [];
    var selfMatches =
      !query ||
      normalize(item.name).indexOf(query) !== -1;
    var showAllDescendants = ancestorMatched || selfMatches;
    var visibleChildren = children.filter(function (child) {
      return (
        showAllDescendants ||
        genreMatches(child, tree, query)
      );
    });

    var node = document.createElement("div");
    var row = document.createElement("div");
    var link = document.createElement("a");
    var meta = document.createElement("span");

    node.className = "ee-genre-node";
    row.className = "ee-genre-row";

    link.className = "ee-genre-link";
    link.href = item.href;
    link.textContent = item.name;

    meta.className = "ee-genre-count";
    meta.textContent =
      item.artistCount.toLocaleString("en") +
      (item.artistCount === 1 ? " artist" : " artists");

    if (visibleChildren.length) {
      var toggle = document.createElement("button");
      var childContainer = document.createElement("div");
      var openForSearch = !!query;

      toggle.type = "button";
      toggle.className = "ee-genre-toggle";
      toggle.setAttribute(
        "aria-label",
        "Toggle " + item.name + " subgenres"
      );
      toggle.setAttribute(
        "aria-expanded",
        openForSearch ? "true" : "false"
      );
      toggle.textContent = "›";

      childContainer.className = "ee-genre-children";
      childContainer.hidden = !openForSearch;

      visibleChildren.forEach(function (child) {
        childContainer.appendChild(
          createGenreNode(
            child,
            tree,
            query,
            showAllDescendants
          )
        );
      });

      toggle.addEventListener("click", function () {
        var open =
          toggle.getAttribute("aria-expanded") !== "true";

        toggle.setAttribute(
          "aria-expanded",
          open ? "true" : "false"
        );
        childContainer.hidden = !open;
      });

      row.appendChild(toggle);
      node.appendChild(row);
      node.appendChild(childContainer);
    } else {
      var spacer = document.createElement("span");
      spacer.className = "ee-genre-toggle-spacer";
      row.appendChild(spacer);
      node.appendChild(row);
    }

    row.appendChild(link);
    row.appendChild(meta);

    return node;
  }

  function renderGenreTree(section, items, tree, query) {
    var results = section.querySelector(".ee-index-results");
    var normalizedQuery = normalize(query);

    results.innerHTML = "";

    var visibleRoots = tree.roots.filter(function (root) {
      return genreMatches(root, tree, normalizedQuery);
    });

    if (!visibleRoots.length) {
      var empty = document.createElement("p");

      empty.className = "ee-index-empty";
      empty.textContent = "No matches found.";
      results.appendChild(empty);
      return;
    }

    visibleRoots.forEach(function (root) {
      results.appendChild(
        createGenreNode(root, tree, normalizedQuery, false)
      );
    });
  }

  function setupGenreSection(id, items) {
    var section = document.getElementById(id);

    if (!section) return;

    var input = section.querySelector(".ee-index-search");
    var count = section.querySelector(".ee-index-count");
    var tree = buildGenreTree(items);

    count.textContent =
      items.length.toLocaleString("en") +
      (items.length === 1 ? " genre" : " genres");

    renderGenreTree(section, items, tree, "");
    setupCollapsible(section);

    input.addEventListener("input", function () {
      renderGenreTree(section, items, tree, input.value);
    });
  }

  function attemptRender() {
    if (state.rendered) return;

    var artists = makeArtistItems();
    var venues = makeVenueItems();
    var genres = makeGenreItems();

    state.artists = !!artists;
    state.venues = !!venues;
    state.genres = !!genres;

    if (!state.artists || !state.venues || !state.genres) {
      return;
    }

    state.rendered = true;

    setupGlobalSearch(
      buildGlobalSearchData(artists, venues, genres)
    );
    setupSection("ee-index-artists", artists);
    setupSection("ee-index-venues", venues);
    setupGenreSection("ee-index-genres", genres);
  }

  document.addEventListener("ee:content-index-ready", attemptRender);
  document.addEventListener("ee:concert-data-ready", attemptRender);
  document.addEventListener("ee:venue-data-ready", attemptRender);
  document.addEventListener("ee:genre-data-ready", attemptRender);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attemptRender);
  } else {
    attemptRender();
  }
}());
