(function () {
  "use strict";
  var config = Object.assign({allOccurrences:false, rootSelector:".post-body, .entry-content", optOutSelector:"[data-ee-no-autolink], .ee-no-autolink"}, window.ElectricEyeAutoLinkConfig || {});
  var skip = "a,script,style,noscript,code,pre,button,input,select,textarea,iframe,object,embed,nav,[role='navigation'],[role='button'],.widget,.ad,.adsbygoogle," + config.optOutSelector;
  function escapeRegExp(value) { return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function run() {
    var data = window.ElectricEyeArtistLookup;
    if (!data || document.documentElement.dataset.eeAutolinked) return;
    document.documentElement.dataset.eeAutolinked = "1";
    var terms = data.terms || {}, termSlugs = {}, aliases = Object.keys(terms).sort(function (a,b) { return b.length-a.length; });
    aliases.forEach(function (term) { termSlugs[term.toLocaleLowerCase()] = terms[term]; });
    if (!aliases.length) return;
    var pattern = new RegExp("(^|[^\\p{L}\\p{N}])(" + aliases.map(escapeRegExp).join("|") + ")(?=$|[^\\p{L}\\p{N}])", "giu");
    var linked = new Set();
    document.querySelectorAll(config.rootSelector).forEach(function (root) {
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), nodes = [], node;
      while ((node = walker.nextNode())) if (node.nodeValue.trim() && !node.parentElement.closest(skip)) nodes.push(node);
      nodes.forEach(function (textNode) {
        pattern.lastIndex = 0; var source = textNode.nodeValue, fragment = document.createDocumentFragment(), last = 0, match, changed = false;
        while ((match = pattern.exec(source))) {
          var slug = termSlugs[match[2].toLocaleLowerCase()];
          if (!slug || (!config.allOccurrences && linked.has(slug))) continue;
          var start = match.index + match[1].length;
          fragment.append(document.createTextNode(source.slice(last,start)));
          var link = document.createElement("a"); link.className="ee-artist-autolink"; link.href=data.artistPage+encodeURIComponent(slug); link.textContent=match[2]; fragment.append(link);
          last = start + match[2].length; linked.add(slug); changed = true;
        }
        if (changed) { fragment.append(document.createTextNode(source.slice(last))); textNode.replaceWith(fragment); }
      });
    });
  }
  document.addEventListener("ee:artist-lookup-ready", run);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run, {once:true}); else run();
}());
