(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2087f7b5d361d154.js","sha256":"2087f7b5d361d154d54f97649286d82209ddaa0513bf7eb56cc2f8688bca2514","count":1980,"publishedAt":"2026-11-08T17:46:53Z","state":"calendar-state.json","stateSha256":"1efbfb09715fe04693faddc09ac1619281ecba3f8ce50e4134b5655ab6fac02a","sourceState":"calendar-source-state.json","sourceStateSha256":"367305fdcb2df1dd5b64bdf93513787c97f5f63bed9248b8baca94f5b09461d3"});
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
