(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5ab560b36614f60c.js","sha256":"5ab560b36614f60c33cd6d52c9257a84700e6257d97d6fd263c5627c70fea268","count":2237,"publishedAt":"2026-09-03T00:04:19Z","state":"calendar-state.json","stateSha256":"e7e63d4663c4ea326bbcbf131d4a87361cc1efa6ef3100d1417a27a7b33f38f4"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
